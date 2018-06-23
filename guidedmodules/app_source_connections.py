###########################################################
# App Source Connections
#
# This module defines the abstract AppSourceConnection
# class and its subclasses which fetch app definitions from
# local directories and remote locations like git
# repositories.
#
# The main implementation is the PyFsAppSourceConnection,
# which reads apps from directories in a PyFilesystem2
# directory. We then use fs.osfs and our own fs classes
# that implement filesystems around the the PyGithub and
# GitPython packages.
#
# The AppSourceConnection has two methods, one to fetch all
# apps and one to get an app by name, both returning
# instances of App, an abstract class defined here as well.
# There is one implementation, PyFsApp, which returns app
# data by reading a PyFilesystem2 directory, which allows
# us to nicely pull app data from any local/remote location
# as long as we can access it with PyFilesystem2.
#
# Each AppSourceConnection implementation is configured by
# passing it an AppSource instance. The AppSource's "spec"
# property holds a dict holding key/value data, such as the
# local directory path or a git repository and credentials.
# AppSourceConnection.create(source) creates an AppSourceConnection
# instance by reading source.spec["type"] to determine which
# class to instantiate and then passing the source to the
# appropriate implementation. See comments below for details
# about what should be in source.spec.
#
# AppSourceConnections should be used in with ...: blocks
# so that resources opened by the connection are automatically
# closed.
###########################################################

import re

import fs, fs.errors
from fs.base import FS as fsFS

from .app_loading import ModuleDefinitionError

class AppSourceConnectionError(Exception):
    pass

class AppSourceConnection(object):
    """An AppSourceConnection provides methods to access apps in an AppSource."""

    @staticmethod
    def create(source):
        """Returns a new AppSourceConnection instance given an AppSource."""
        if source.spec.get("type") in AppSourceConnectionTypes:
            return AppSourceConnectionTypes[source.spec["type"]](source)
        raise ValueError("Invalid AppSourceConnection type: %s" % repr(source.spec.get("type")))

    def list_apps(self):
        raise Exception("Not implemented!")
    def get_app(self, name):
        raise Exception("Not implemented!")

class App(object):
    """An App is a remote definition of Modules and
    associated resources."""

    def __init__(self, store, name):
        self.store = store
        self.name = name

    def __repr__(self):
        return "<App {name} in {store}>".format(name=self.name, store=self.store)

    def get_catalog_info(self):
        raise Exception("Not implemented!")
    def get_modules(self):
        raise Exception("Not implemented!")
    def get_assets(self):
        raise Exception("Not implemented!")


### IMPLEMENTATIONS ###

# This class implements AppSourceConnection for an empty
# set of apps. source.spec should look like:
# {
#  "type": "null"
# }
class NullAppSourceConnection(AppSourceConnection):
    """The NullAppSourceConnection contains no apps."""
    def __init__(self, source):
        pass
    def __enter__(self): return self
    def __exit__(self, *args): return
    def __repr__(self): return "<NullAppSourceConnection>"
    def list_apps(self):
        return
        yield # make a generator


class MultiplexedAppSourceConnection(AppSourceConnection):
    """A subclass of AppSourceConnection that wraps other AppSourceConnection instances."""

    def __init__(self, sources):
        self.loaders = []
        for ms in sources:
            try:
                self.loaders.append(AppSourceConnection.create(ms))
            except ValueError as e:
                raise ValueError('There was an error creating the AppSource "{}": {}'.format(ms.slug, e))

    # Override "with ...:" semantics to enter and exit all of the
    # connections this connection wraps.
    def __enter__(self):
        for loader in self.loaders:
            loader.__enter__()
        return self
    def __exit__(self, *args):
        exceptions = []
        for loader in self.loaders:
            try:
                loader.__exit__(None, None, None)
            except Exception as e:
                exceptions.append((loader, e))
        if exceptions:
            raise Exception(exceptions)

    def __repr__(self):
        return "<MultiplexedAppSourceConnection %s>" % repr(self.loaders)

    def list_apps(self):
        # List all of the apps in all of the stores.
        for ms in self.loaders:
            for app in ms.list_apps():
                yield app

class PyFsAppSourceConnection(AppSourceConnection):
    """Creates a connection from a Pyfilesystem2 filesystem, like
    a local directory containing directories for apps."""

    def __init__(self, source, fsfunc):
        # Don't initialize the filesystem yet - just store the
        # class and __init__ arguments.
        self.source = source
        self.fsfunc = fsfunc

    def __enter__(self):
        # Initialize at the start of the "with" block that this
        # object is used in.
        try:
            # Open the filesystem.
            self.root = self.fsfunc()
        except (fs.errors.CreateFailed, fs.errors.ResourceNotFound) as e:
            raise AppSourceConnectionError(
                'There was an error accessing the AppSource "{}" which connects to {}. The error was: {}'.format(
                    self.source.slug,
                    self.source.get_description(),
                    str(e)
                ))

        # Open catalog.yaml, which contains metadata attached to the apps.
        self.catalog = self.load_catalog_file()

        return self

    def __exit__(self, *args):
        # Clean up the filesystem object at the end of the "with"
        # block.
        if self.root:
            self.root.close()

    def __repr__(self):
        return "<AppSourceConnection {src}>".format(src=self.source.get_description())

    def load_catalog_file(self):
        # Load catalog.yaml.
        try:
            with self.root.open("catalog.yaml") as f:
                catalog = read_yaml_file(f)
        except fs.errors.ResourceNotFound:
            catalog = { }

        # Ensure 'apps' key exists.
        if not isinstance(catalog.get("apps"), dict):
            catalog["apps"] = {}

        return catalog

    def list_apps(self):
        # Every directory is an app containing app.yaml file
        # which is the app's root module YAML.
        for entry in self.root.scandir(""):
            # Is this a valid app directory?
            if not entry.is_dir: continue
            if "app.yaml" not in self.root.listdir(entry.name): continue

            # Yield an app instance.
            yield PyFsApp(
                self,
                entry.name,
                self.root.opendir(entry.name))

    def get_app(self, name):
        # Is this a valid app name? Force evaluation of scandir
        # to check that the app directory and an app.yaml exist.
        try:
            if "app.yaml" not in self.root.listdir(name):
                raise fs.errors.ResourceNotFound()
        except fs.errors.ResourceNotFound:
            raise ValueError("App {} not found in {} ({}).".format(
                name,
                self.source.slug,
                self.source.get_description(),
            ))
        return PyFsApp(
            self,
            name,
            self.root.opendir(name))

    def get_app_catalog_info(self, app):
        ret = {
            # All apps from a filesystem-based store require no credentials
            # to get their contents because... we already got their contents.
            "authz": "none",

            # Add a 'published' key that comes from the catalog.yaml file.
            "published": self.catalog["apps"].get(app.name),
        }
        return ret

class PyFsApp(App):
    """An App whose modules and assets are stored in a directory
       layout rooted at a PyFilesystem2 file system."""
    
    def __init__(self, store, name, fs):
        super().__init__(store, name)
        self.fs = fs

    def get_catalog_info(self):
        # Load the app.yaml file and return its catalog information.
        with self.fs.open("app.yaml") as f:
            err_str = "%s/app.yaml" % self.fs.desc('')
            try:
                yaml = read_yaml_file(f)
            except ModuleDefinitionError as e:
                raise ModuleDefinitionError("There was an error loading the module at %s: %s" % (
                    err_str,
                    str(e)))
            except Exception as e:
                raise ModuleDefinitionError("There was an unhandled error loading the module at %s." % (
                    err_str,
                    str(e)))

        # Construct catalog info.
        ret = { }

        # Start with the catalog information and protocol stored in the app.yaml.
        ret["title"] = yaml["title"]
        ret.update(yaml.get("catalog", {}))
        if "protocol" in yaml: ret["protocol"] = yaml["protocol"]

        # Load an optional README.md which provides the app's long description.
        try:
            # Read the README.md.
            with self.fs.open("README.md") as f:
                readme = f.read()

            # Strip any initial heading that has the app name itself, since
            # that is expected to not be included in the long description.
            # Check both CommonMark heading formats.
            readme = re.sub(r"^\s*#+ *" + re.escape(ret["title"]) + r"\s*", "", readme)
            readme = re.sub(r"^\s*" + re.escape(ret["title"]) + r"\s*[-=]+\s*", "", readme)

            ret.setdefault("description", {})["long"] = readme
        except fs.errors.ResourceNotFound:
            pass

        # Override with source-specified catalog information.
        ret.update(self.store.get_app_catalog_info(self))

        # Set non-overridable fields.
        ret.update({
            "name": self.name,
        })
        if "icon" in yaml:
            try:
                with self.fs.open("assets/" + yaml["icon"], "rb") as f:
                    ret["app-icon"] = f.read()
            except fs.errors.ResourceNotFound:
                pass

        return ret

    def get_modules(self):
        # Return a generator over parsed YAML data for modules.
        return self.iter_modules([])

    def iter_modules(self, path):
        from os.path import splitext
        path_entries = self.fs.listdir('/'.join(path))
        for entry in self.fs.scandir('/'.join(path)):
            if not entry.is_dir:
                # If this is a file that ends in .yaml, it is a module file.
                # Strip the extension and construct a module ID that concatenates
                # the path on disk and the file name.
                fn_name, fn_ext = splitext(entry.name)
                if fn_ext == ".yaml":
                    # The module ID combines its local path and the filename.
                    module_id = "/".join(path + [fn_name])

                    # Read the YAML file.
                    with self.fs.open(entry.name) as f:
                        module_spec = read_yaml_file(f)

                    yield (module_id, module_spec)

            elif entry.name in ("assets", "private-assets"):
                # Don't recurisvely walk into directories named 'assets' or
                # 'private-assets'. These directories provide static assets
                # that go along with the modules in that directory. 'assets'
                # are public assets that are exposed by the web server.
                pass

            else:
                # Recursively walk directories.
                for module in self.iter_modules(path+[entry.name]):
                    yield module

    def get_assets(self):
        if "assets" in self.fs.listdir(''):
            for asset in PyFsApp.iter_assets(self.fs, []):
                yield asset

    @staticmethod
    def iter_assets(fs, path):
        import hashlib # for filesystems that don't provide this info
        import os.path # for join because we return virtual unixy paths

        for entry in fs.scandir("/".join(["assets"] + path)):
            if entry.is_dir:
                for asset in iter_assets(fs, path+[entry.name]):
                    yield asset
            else:
                fn = "/".join(path + [entry.name])

                with fs.open("assets/" + fn, "rb") as f:
                    m = hashlib.sha256()
                    while True:
                        data = f.read(8192)
                        if not data: break
                        m.update(data)
                    content_hash = m.hexdigest()

                def make_content_loader(fn):
                    def content_loader():
                        with fs.open("assets/" + fn, "rb") as f:
                            return f.read()
                    return content_loader

                yield (fn, content_hash, make_content_loader(fn))


# This class implements AppSourceConnection for a local path using fs.osfs.OSFS.
# source.spec should look like:
# {
#  "type": "local",
#  "path": "path/to/apps",
# }
class LocalDirectoryAppSourceConnection(PyFsAppSourceConnection):
    """An App Store provided by a local directory."""
    def __init__(self, source):
        from fs.osfs import OSFS
        super().__init__(source, lambda : OSFS(source.spec["path"]))


class SimplifiedReadonlyFilesystem(fsFS):
    def listdir(self, path):
        return [entry.name for entry in self.scandir(path)]
    def getinfo(self, path, namespaces=[]):
        parent_path = "/".join(path.split("/")[:-1])
        name = path.split("/")[-1]
        for entry in self.scandir(parent_path):
            if entry.name == name:
                return entry
        raise ValueError("Path not found.")
    def makedir(self, *args): raise Exception("Not implemented.")
    def remove(self, *args): raise Exception("Not implemented.")
    def removedir(self, *args): raise Exception("Not implemented.")
    def setinfo(self, *args): raise Exception("Not implemented.")


class GithubApiFilesystem(SimplifiedReadonlyFilesystem):
    """
      { "type": "github", "repo": "orgname/reponame", ["path": "/subpath",] "auth": { "user": "...", "pw": "..." } }
    """

    def __init__(self, repo, path, user, pw):
        # Create client.
        from github import Github
        g = Github(user, pw)
        self.repo = g.get_repo(repo)
        self.path = (path or "") + "/"

        # Run a quick call to check access.
        from github.GithubException import GithubException
        try:
            self.repo.get_dir_contents(self.path)
        except GithubException as e:
            raise fs.errors.CreateFailed(e.data.get("message"))

    def scandir(self, path, namespaces=None, page=None):
        from fs.info import Info
        for cf in self.repo.get_dir_contents(self.path + path):
            yield Info({
                "basic": {
                    "name": cf.name,
                    "is_dir": cf.type == "dir",
                },
                "hash": {
                    "sha1": cf.sha,
                }
            })

    def openbin(self, path, mode="r", **options):
        if mode not in ("r", "rb"): raise ValueError("Invalid open mode. Must be 'r' or 'rb'.")
        import base64, io
        cf = self.repo.get_contents(self.path + path)
        if cf.type != "file": raise ValueError("path is a directory")
        if cf.encoding != "base64": raise ValueError("content encoding is unrecognized")
        content = base64.b64decode(cf.content)
        return io.BytesIO(content)


# This class implements AppSourceConnection using the GitHub API,
# using the GithubApiFilesystem class above to wrap the GitHub API
# in a PyFilesystem2 filesystem. source.spec should look like:
# {
#	"type": "github",
#   "repo": "organization/repository",
#   "path": "apps", # optional
#   "auth": { "user": "username", "pw": "password" } # optional
# }
class GithubApiAppSourceConnection(PyFsAppSourceConnection):
    def __init__(self, source):
        # the spec is incomplete
        if not isinstance(source.spec.get("repo"), str): raise ValueError("The AppSource is misconfigured: missing or invalid 'repo'.")
        if not isinstance(source.spec.get("path"), (str, type(None))): raise ValueError("The AppSource is misconfigured: missing or invalid 'path'.")
        if not (isinstance(source.spec.get("auth"), dict) and isinstance(source.spec["auth"].get("user"), str)): raise ValueError("The AppSource is misconfigured: missing or invalid 'auth.user'.")
        if not (isinstance(source.spec.get("auth"), dict) and isinstance(source.spec["auth"].get("pw"), str)): raise ValueError("The AppSource is misconfigured: missing or invalid 'auth.pw'.")
        super().__init__(source, lambda : GithubApiFilesystem(
            source.spec["repo"], source.spec.get("path"),
            source.spec["auth"]["user"], source.spec["auth"]["pw"]))


class GitRepositoryFilesystem(SimplifiedReadonlyFilesystem):
    def __init__(self, url, branch, path, ssh_key=None):
        self.url = url
        self.branch = branch or None
        self.path = (path or "") + "/"
        self.ssh_key = ssh_key

        # Create a local git working directory.
        import tempfile
        self.tempdir_obj = tempfile.TemporaryDirectory()
        self.tempdir = self.tempdir_obj.__enter__()

        self.description = self.url + "/" + self.path.strip("/")
        if self.branch:
            self.description += "@" + self.branch

        # Validate access.
        self.getdir("")

    def __repr__(self):
        return "<gitfs '%s'>" % self.description

    def close(self):
        # Release the temporary directory.
        self.tempdir_obj.__exit__(None, None, None)

    def get_repo_root(self):
        # Return cached tree.
        if hasattr(self, "repo_root_tree"):
            return self.repo_root_tree

        import os, os.path
        import git

        # Create an empty git repo in the temporary directory.
        self.repo = git.Repo.init(self.tempdir)

        # Make SSH non-interactive.
        ssh_options = "ssh -o StrictHostKeyChecking=no -o BatchMode=yes"

        # If an SSH key is provided, store it in the temporary directory and
        # then use it.
        if self.ssh_key:
            ssh_key_file = os.path.join(self.tempdir, "ssh.key")
            old_umask = os.umask(0o077) # ssh requires group/world permissions to be zero
            try:
                with open(ssh_key_file, "wb") as f:
                    f.write(self.ssh_key.encode("ascii"))
            finally:
                os.umask(old_umask)
            ssh_options += " -i " + ssh_key_file

        self.repo.git.environment()["GIT_SSH_COMMAND"] = ssh_options

        # For debugging, log a command that we could try on the command line.
        #print("SSH_COMMAND=\"{ssh_options}\" git fetch --depth 1 {url} {branch}".format(
        #    ssh_options=ssh_options, url=self.url, branch=self.branch), file=sys.stderr)

        # Fetch.
        import git.exc
        try:
            self.repo.git.execute(
                [
                    self.repo.git.git_exec_name,
                    "fetch",
                    "--depth", "1", # avoid getting whole repo history
                    self.url, # repo URL
                    self.branch or "", # branch to fetch
                ], kill_after_timeout=20)
        except git.exc.GitCommandError as e:
            # This is where errors occur, which is hopefully about auth.
            raise fs.errors.CreateFailed("The repository URL is either not valid, not public, or ssh_key was not specified or not valid (%s)." % e.stderr)

        # Get the tree for the remote branch's HEAD.
        tree = self.repo.tree("FETCH_HEAD")

        # The Pythonic way would be to add a remote for the remote repository, run
        # fetch, and then access its ref.
        #self.remote = self.repo.create_remote("origin", self.spec["url"])
        #self.remote.fetch(self.spec.get("branch"))
        #tree = self.repo.tree(self.remote.refs[0])

        # If a path was given, move to that subdirectory.
        # TODO: Check that paths with subdirectories that have no other content
        # but an inner subdirectory work, because git does something funny about
        # flattening empty directories.
        for pathitem in self.path.split("/"):
            if pathitem != "":
                tree = tree[pathitem]

        # Cache and return it.
        self.repo_root_tree = tree
        return tree

    def getdir(self, path):
        tree = self.get_repo_root()
        for item in path.split("/"):
            if item != "":
                try:
                    tree = tree[item] # TODO: As above.
                except KeyError:
                    raise fs.errors.ResourceNotFound(path)
        return tree

    def scandir(self, path, namespaces=None, page=None):
        # Get the root tree and then move to the desired subdirectory.
        from fs.info import Info
        tree = self.getdir(path)
        for item in tree:
            if item.type not in ("tree", "blob"): continue
            yield Info({
                "basic": {
                    "name": item.name,
                    "is_dir": item.type == "tree",
                },
                "hash": {
                    "sha1": item.hexsha,
                }
            })

    def openbin(self, path, mode="r", **options):
        # Get the root tree and then move to the desired item.
        if mode not in ("r", "rb"): raise ValueError("Invalid open mode. Must be 'r' or 'rb'.")
        import io
        tree = self.getdir(path)
        return io.BytesIO(tree.data_stream.read())


# This class implements AppSourceConnection for a git repository,
# using the GitRepositoryFilesystem class above to wrap the git client
# in a PyFilesystem2 filesystem. source.spec should look like:
# {
#  "type": "git",
#  "url": "git@github.com:GovReady/myrepository",
#  "branch": "master", # optional - remote's default branch is used by default
#  "path": "/subpath", # this is optional, if specified it's the directory in the repo to look at
#  "ssh_key": "-----BEGIN RSA PRIVATE KEY-----\nkey data\n-----END RSA PRIVATE KEY-----"
#             ^ for private repos only
# }
class GitRepositoryAppSourceConnection(PyFsAppSourceConnection):
    """An App Store provided by a local directory."""
    def __init__(self, source):
        # validate spec
        if not isinstance(source.spec.get("url"), str): raise ValueError("The AppSource is misconfigured: missing or invalid 'url'.")
        if not isinstance(source.spec.get("branch"), (str, type(None))): raise ValueError("The AppSource is misconfigured: missing or invalid 'url'.")
        if not isinstance(source.spec.get("path"), (str, type(None))): raise ValueError("The AppSource is misconfigured: missing or invalid 'path'.")
        super().__init__(source, lambda : GitRepositoryFilesystem(
            source.spec["url"], source.spec.get("branch"), source.spec.get("path"),
            source.spec.get("ssh_key")))


def read_yaml_file(f):
    # Use the safe YAML loader via rtyaml, which loads mappings with
    # OrderedDicts so that order is not lost, and catch errors.
    import rtyaml, yaml.scanner, yaml.parser, yaml.constructor
    try:
        return rtyaml.load(f)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError, yaml.constructor.ConstructorError) as e:
        raise ModuleDefinitionError("There was an error parsing the YAML file: " + str(e))

AppSourceConnectionTypes = {
    "null": NullAppSourceConnection,
    "local": LocalDirectoryAppSourceConnection,
    "github": GithubApiAppSourceConnection,
    "git": GitRepositoryAppSourceConnection,
}
