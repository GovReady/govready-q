from django.db import transaction
from django.db.models.deletion import ProtectedError

from collections import OrderedDict
import enum
import json
import sys

import fs
from fs.base import FS as fsFS

from .models import AppSource, AppInstance, Module, ModuleQuestion, ModuleAssetPack, ModuleAsset, Task
from .validate_module_specification import validate_module, ValidationError as ModuleValidationError

class AppImportUpdateMode(enum.Enum):
    CreateInstance = 1
    ForceUpdate = 2
    CompatibleUpdate = 3

class ModuleDefinitionError(Exception):
    pass

class AppSourceConnectionError(Exception):
    pass

class AppSourceConnection(object):
    """An AppSourceConnection provides methods to access apps in an AppSource."""

    @staticmethod
    def create(source):
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

    @transaction.atomic # there can be an error mid-way through updating a Module
    def import_into_database(self, update_mode=AppImportUpdateMode.CreateInstance, update_appinst=None):
        # Get or create a ModuleAssetPack first, since there is a foriegn key
        # from Modules to ModuleAssetPacks.
        asset_pack = load_module_assets_into_database(self)

        # Pull in all of the modules. We need to know them all because they'll
        # be processed recursively.
        available_modules = dict(self.get_modules())

        # Create an AppInstance to add new Modules into, unless update_appinst is given.
        if update_appinst is None:
            appinst = AppInstance.objects.create(
                source=self.store.source,
                appname=self.name,
            )
        else:
            # Update Modules in this one.
            appinst = update_appinst

        # Load them all into the database. Each will trigger load_module_into_database
        # for any modules it depends on.
        processed_modules = { }
        for module_id in available_modules.keys():
            load_module_into_database(
                self,
                appinst,
                module_id,
                available_modules, processed_modules,
                [], asset_pack, update_mode)

        return appinst


### IMPLEMENTATIONS ###

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
    """A subclass of ModuleLoader that wraps other ModuleLoader classes
       at given mount-points in the module naming space."""

    def __init__(self, sources):
        self.loaders = []
        for ms in sources:
            try:
                self.loaders.append(AppSourceConnection.create(ms))
            except ValueError as e:
                raise ValueError('There was an error creating the AppSource "{}": {}'.format(ms.slug, e))

    # Override "with ...:" semantics
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
    """Creates an app store from a Pyfilesystem2 filesystem, like
    a local directory containing directories for apps."""

    def __init__(self, source, fsfunc):
        # Don't initialize the filesystem yet - just store the
        # class and __init__ arguments.
        self.source = source
        self.fsfunc = fsfunc

    def __enter__(self):
        # Initialize at the start of the "with" block that this
        # object is used in.
        import fs.errors
        try:
            self.root = self.fsfunc()
        except AppSourceConnectionError as e:
            raise AppSourceConnectionError(
                'There was an error accessing the AppSource "{}" which connects to {}. The error was: {}'.format(
                    self.source.slug,
                    self.source.get_description(),
                    str(e)
                ))
        return self
    def __exit__(self, *args):
        # Clean up the filesystem object at the end of the "with"
        # block.
        if self.root:
            self.root.close()

    def __repr__(self):
        return "<AppSourceConnection {src}>".format(src=self.source.get_description())

    def list_apps(self):
        # Every directory is an app containing app.yaml
        # which is the app's root module YAML.
        for entry in self.root.scandir(""):
            if entry.is_dir:
                # Check for presence of app.yaml.
                if "app.yaml" in self.root.listdir(entry.name):
                    yield PyFsApp(
                        self,
                        entry.name,
                        self.root.opendir(entry.name))

    def get_app(self, name):
        if len(list(self.root.scandir(name))) == 0:
            raise ValueError("App not found.")
        return PyFsApp(self,
            name,
            self.root.opendir(name))

    def get_app_catalog_info(self, app):
        # All apps from a filesystem-based store require no credentials
        # to get their contents because... we already got their contents.
        return {
            "authz": "none",
        }

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
        ret = {
            "name": self.name,
            "title": yaml["title"],
        }
        ret.update(yaml.get("catalog", {}))
        ret.update(self.store.get_app_catalog_info(self))
        if "protocol" in yaml: ret["protocol"] = yaml["protocol"]

        # Load the app icon.
        if "icon" in yaml:
            import fs.errors
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
            raise AppSourceConnectionError(msg=e.data.get("message"))

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


class GithubApiAppSourceConnection(PyFsAppSourceConnection):
    """An App Store provided by a local directory."""
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
    """
        "url": "git@github.com:GovReady/myrepository",
        "branch": "master", # optional - remote's default branch is used by default
        "path": "/subpath", # this is optional, if specified it's the directory in the repo to look at
        "ssh_key": "-----BEGIN RSA PRIVATE KEY-----\nkey data\n-----END RSA PRIVATE KEY-----"
            # ^ for private repos only
    """

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
            raise AppSourceConnectionError("The repository URL is either not valid, not public, or ssh_key was not specified or not valid (%s)." % e.stderr)

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
        import fs.errors
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


## LOAD MODULES ##


class ValidationError(ModuleDefinitionError):
    def __init__(self, file_name, scope, message):
        super().__init__("There was an error in %s (%s): %s" % (file_name, scope, message))

class CyclicDependency(ModuleDefinitionError):
    def __init__(self, path):
        super().__init__("Cyclic dependency between modules: " + " -> ".join(path + [path[0]]))

class DependencyError(ModuleDefinitionError):
    def __init__(self, from_module, to_module):
        super().__init__("Invalid module ID '%s' in module '%s'." % (to_module, from_module))

class IncompatibleUpdate(Exception):
    pass

def load_module_into_database(app, appinst, module_id, available_modules, processed_modules, dependency_path, asset_pack, update_mode):
    # Prevent cyclic dependencies between modules.
    if module_id in dependency_path:
        raise CyclicDependency(dependency_path)

    # Because of dependencies between modules, we may have already
    # been here. Do this after the cyclic dependency check or else
    # we would never see a cyclic dependency.
    if module_id in processed_modules:
        return processed_modules[module_id]

    # Load the module's YAML file.
    if module_id not in available_modules:
        raise DependencyError((dependency_path[-1] if len(dependency_path) > 0 else None), module_id)

    spec = available_modules[module_id]

    # Sanity check that the 'id' in the YAML file matches just the last
    # part of the path of the module_id. This allows the IDs to be 
    # relative to the path in which the module is found.
    if spec.get("id") != module_id.split('/')[-1]:
        raise ValidationError(module_id, "module", "Module 'id' field (%s) doesn't match source file path (\"%s\")." % (repr(spec.get("id")), module_id))

    # Replace spec["id"] (just the last part of the path) with the full module_id
    # (a full path, minus .yaml) relative to the root of the app. The id is used
    # in validate_module to resolve references to other modules.
    spec["id"] = module_id

    # Validate and normalize the module specification.

    try:
        spec = validate_module(spec)
    except ModuleValidationError as e:
        raise ValidationError(spec['id'], e.context, e.message)

    # Recursively update any modules this module references.
    dependencies = { }
    for m1 in get_module_spec_dependencies(spec):
        mdb = load_module_into_database(app, appinst, m1, available_modules, processed_modules, dependency_path + [spec["id"]], asset_pack, update_mode)
        dependencies[m1] = mdb

    # Now that dependent modules are loaded, replace module string IDs with database numeric IDs.
    for q in spec.get("questions", []):
        if q.get("type") not in ("module", "module-set"): continue
        if "module-id" not in q: continue
        mdb = dependencies[q["module-id"]]
        q["module-id"] = mdb.id

    # Look for an existing Module to update.

    m = None
    if update_mode != AppImportUpdateMode.CreateInstance:
        try:
            m = Module.objects.get(app=appinst, module_name=spec['id'])
        except Module.DoesNotExist:
            # If it doesn't exist yet in the previous app, we'll just create it.
            pass
    if m:
        # What is the difference between the app's module and the module in the database?
        change = is_module_changed(m, app.store.source, spec, asset_pack)
    
        if change is None:
            # There is no difference, so we can go on immediately.
            pass

        elif (change is False and update_mode == AppImportUpdateMode.CompatibleUpdate) \
            or update_mode == AppImportUpdateMode.ForceUpdate:
            # There are no incompatible changes and we're allowed to update modules,
            # or we're forcing an update and it doesn't matter whether or not there
            # are changes --- update this one in place.
            update_module(m, spec, asset_pack, True)

        else:
            # Block an incompatible update --- don't create a new module.
            raise IncompatibleUpdate("Module {} cannot be updated because changes are incompatible with the existing data model: {}".format(module_id, change))

    if not m:
        # No Module in the database matched what we need, or an existing
        # one cannot be updated. Create one.
        m = create_module(app, appinst, spec, asset_pack)

    processed_modules[module_id] = m
    return m


def get_module_spec_dependencies(spec):
    # Scans a module YAML specification for any dependencies and
    # returns a generator that yields the module IDs of the
    # dependencies.
    questions = spec.get("questions")
    if not isinstance(questions, list): questions = []
    for question in questions:
        if question.get("type") in ("module", "module-set"):
            if "module-id" in question:
                yield question["module-id"]


def create_module(app, appinst, spec, asset_pack):
    # Create a new Module instance.
    m = Module()
    m.source = app.store.source
    m.app = appinst
    m.module_name = spec['id']
    print("Creating", m.app, m.module_name, file=sys.stderr)
    update_module(m, spec, asset_pack, False)
    return m


def remove_questions(spec):
    spec = OrderedDict(spec) # clone
    if "questions" in spec:
        del spec["questions"]
    return spec


def update_module(m, spec, asset_pack, log_status):
    # Update a module instance according to the specification data.
    # See is_module_changed.
    if log_status:
        print("Updating", repr(m), file=sys.stderr)

    # Remove the questions from the module spec because they'll be
    # stored with the ModuleQuestion instances.
    m.visible = True
    m.spec = remove_questions(spec)
    m.assets = asset_pack
    m.save()

    # Update its questions.
    qs = set()
    for i, question in enumerate(spec.get("questions", [])):
        qs.add(update_question(m, i, question, log_status))

    # Delete removed questions (only happens if the Module is
    # not yet in use).
    for q in m.questions.all():
        if q not in qs:
            print("Deleting", repr(q), file=sys.stderr)
            try:
                q.delete()
            except ProtectedError:
                raise IncompatibleUpdate("Module {} cannot be updated because question {}, which has been removed, has already been answered.".format(m.module_name, q.key))

    # If we're updating a Module in-place, clear out any cached state on its Tasks.
    for t in Task.objects.filter(module=m):
        t.on_answer_changed()


def update_question(m, definition_order, spec, log_status):
    # Adds or updates a ModuleQuestion within Module m given its
    # YAML specification data in 'question'.

    # Create/update database record.
    field_values = {
        "definition_order": definition_order,
        "spec": spec,
        "answer_type_module": Module.objects.get(id=spec["module-id"]) if spec.get("module-id") else None,
    }
    q, isnew = ModuleQuestion.objects.get_or_create(
        module=m,
        key=spec["id"],
        defaults=field_values)

    if isnew:
        pass # print("Added", repr(q))
    else:            
        # Don't need to update the database (and we can avoid
        # bumping the .updated date) if the question's specification
        # is identifical to what's already stored.
        if is_question_changed(q, definition_order, spec) is not None:
            if log_status: print("Updated", repr(q), file=sys.stderr)
            for k, v in field_values.items():
                setattr(q, k, v)
            q.save(update_fields=field_values.keys())

    return q


def is_module_changed(m, source, spec, asset_pack):
    # Returns whether a module specification has changed since
    # it was loaded into a Module object (and its questions).
    # Returns:
    #   None => No change.
    #   False => Change, but is compatible with the database record
    #           and the database record can be updated in-place.
    #   any string => Incompatible change - a new database record is needed.

    # If all other metadata is the same, then there are no changes.
    if \
            json.dumps(m.spec, sort_keys=True) == json.dumps(remove_questions(spec), sort_keys=True) \
        and m.assets == asset_pack \
        and json.dumps([q.spec for q in m.get_questions()], sort_keys=True) \
            == json.dumps([q for q in spec.get("questions", [])], sort_keys=True):
        return None

    # Now we're just checking if the change is compatible or not with
    # the existing database record.

    if m.spec.get("version") != spec.get("version"):
        # The module writer can force a bump by changing the version
        # field.
        return "The module version number changed, forcing a reload."

    # If there are no Tasks started for this Module, then the change is
    # compatible because there is no data consistency to worry about.
    if not Task.objects.filter(module=m).exists():
        return False

    # An incompatible change is the removal of a question, the change
    # of a question type, or the removal of choices from a choice
    # question --- anything that would cause a TaskQuestion/TaskAnswer
    # to have invalid data. If a question has never been answered, then
    # this does not apply because there is no data that would become
    # corrupted.
    qs = set()
    for definition_order, q in enumerate(spec.get("questions", [])):
        mq = ModuleQuestion.objects.filter(module=m, key=q["id"]).first()
        if not mq:
            # This is a new question. That's a compatible change.
            continue

        # Is there an incompatible change in the question? (If there
        # is a change that is compatible, we will return that the
        # module is changed anyway at the end of this method.)
        qchg = is_question_changed(mq, definition_order, q)
        if isinstance(qchg, str):
            return "In question %s: %s" % (q["id"], qchg)

        # Remember that we saw this question.
        qs.add(mq)

    # Were any questions removed?
    for mq in m.questions.all():
        if mq in qs:
            continue

        # If this question has never been answered, then anything is fine.
        if mq.taskanswer_set.count() == 0:
            return False

        # The removal of this question is an incompatible change.
        return "Question %s was removed." % mq.key

    # The changes will not create any data inconsistency.
    return False

def is_question_changed(mq, definition_order, spec):
    # Returns whether a question specification has changed since
    # it was loaded into a ModuleQuestion object.
    # Returns:
    #   None => No change.
    #   False => Change, but is compatible with the database record
    #           and the database record can be updated in-place.
    #   str => Incompatible change - a new database record is needed.
    #          The string holds an explanation of what changed.

    # Check if the specifications are identical. We are passed a
    # trasnformed question spec already.
    if mq.definition_order == definition_order \
        and json.dumps(mq.spec, sort_keys=True) == json.dumps(spec, sort_keys=True):
        return None

    # If this question has never been answered, then anything is fine.
    if mq.taskanswer_set.count() == 0:
        return False

    # Change in question type -- that's incompatible.
    if mq.spec["type"] != spec["type"]:
        return "The question type changed from %s to %s." % (
            repr(mq.spec["type"]), repr(spec["type"])
            )

    # Removal of a choice.
    if mq.spec["type"] in ("choice", "multiple-choice"):
        def get_choice_keys(choices): return { c.get("key") for c in choices }
        rm_choices = get_choice_keys(mq.spec["choices"]) - get_choice_keys(spec["choices"])
        if rm_choices:
            return "One or more choices was removed: " + ", ".join(rm_choices) + "."

    # Constriction of valid number of choices to a multiple-choice
    # (min is increased or max is newly set or decreased).
    if mq.spec["type"] == "multiple-choice":
        if "min" not in mq.spec or "max" not in mq.spec:
            return "min/max was missing."
        if spec['min'] > mq.spec['min']:
            return "min went up."
        if mq.spec["max"] is None and spec["max"] is not None:
            return "max was added."
        if mq.spec["max"] is not None and spec["max"] is not None and spec["max"] < mq.spec["max"]:
            return "max went down."

    # Change in the module type if a module-type question, including
    # if the references module has been updated. spec has already
    # been transformed so that it stores an integer module database ID
    # rather than the string module ID in the YAML files.
    if mq.spec["type"] in ("module", "module-set"):
        if mq.spec.get("module-id") != spec.get("module-id"):
            return "The answer type module changed from %s to %s." %(
                repr(mq.spec.get("module-id")), repr(spec.get("module-id"))
            )
        if set(mq.spec.get("protocol", [])) != set(spec.get("protocol", [])):
            return "The answer type protocol changed (%s to %s)." % (
                set(mq.spec.get("protocol")),
                set(spec.get("protocol"))
            )

    # The changes to this question do not create a data inconsistency.
    return False

def load_module_assets_into_database(app):
    # Load all of the static assets from the source into the database.
    # If a ModuleAsset already exists for an asset, use that. If a
    # ModulePack exists for the entire collection of assets, return it
    # and don't create any new database entries.

    source = app.store.source
    assets = list(app.get_assets())

    if len(assets) == 0:
        # Don't bother creating an AssetPack if there are no assets.
        return None

    # Provisionally create a ModuleAssetPack.
    pack = ModuleAssetPack()
    pack.source = source
    pack.basepath = "/"
    pack.trust_assets = source.trust_assets
    pack.paths = {
        file_path: file_hash
        for file_path, file_hash, content_loader
        in assets
    }

    # Compute the total_hash over the pack to see if this already
    # exists as a ModuleAssetPack in the database.
    pack.set_total_hash()

    existing_pack = ModuleAssetPack.objects.filter(
        source=source,
        total_hash=pack.total_hash,
        trust_assets = source.trust_assets).first()
    if existing_pack:
        # Nothing to update.
        return existing_pack

    # Create a new ModuleAssetPack. Save the instance.
    pack.save()

    # Add the assets.
    for file_path, file_hash, content_loader in assets:
        # Get or create the ModuleAsset --- it might already exist in an earlier pack.
        asset, is_new = ModuleAsset.objects.get_or_create(
            source=source,
            content_hash=file_hash,
        )
        if is_new:
            # Set the new file content.
            from django.core.files.base import ContentFile
            asset.file.save(file_path, ContentFile(content_loader()))
            asset.save()

        # Add to the pack.
        pack.assets.add(asset)

    return pack
