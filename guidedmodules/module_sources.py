from django.db import transaction

import enum
import json

import fs
from fs.base import FS as fsFS

from .models import ModuleSource, Module, ModuleQuestion, ModuleAssetPack, ModuleAsset, Task
from .validate_module_specification import validate_module, ValidationError as ModuleValidationError

class AppImportUpdateMode(enum.Enum):
    New = 1
    UpdateIfCompatible = 2
    ForceUpdateInPlace = 3

class ModuleDefinitionError(Exception):
    pass

class AppStore(object):
    """An AppStore is a catalog of Apps."""

    @staticmethod
    def create(source):
        if source.spec.get("type") in AppStoreTypes:
            return AppStoreTypes[source.spec["type"]](source)
        raise ValueError("Invalid AppStore type: %s" % repr(source.spec.get("type")))

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
    def import_into_database(self, update_mode):
        print("Importing", self.store, self.name, "...")

        # Get or create a ModuleAssetPack first, since there is a foriegn key
        # from Modules to ModuleAssetPacks.
        asset_pack = load_module_assets_into_database(self)

        # Pull in all of the modules. We need to know them all because they'll
        # be processed recursively.
        available_modules = dict(self.get_modules())

        # Load them all into the database. Each will trigger load_module_into_database
        # for any modules it depends on.
        processed_modules = { }
        for module_id in available_modules.keys():
            load_module_into_database(
                self,
                module_id,
                available_modules, processed_modules,
                [], asset_pack, update_mode)

        print()

        return processed_modules


### IMPLEMENTATIONS ###

class NullAppStore(AppStore):
    """The NullAppStore contains no apps."""
    def __init__(self, source):
        pass
    def __enter__(self): return self
    def __exit__(self, *args): return
    def __repr__(self): return "<NullAppStore>"
    def list_apps(self):
        return
        yield # make a generator


class MultiplexedAppStore(AppStore):
    """A subclass of ModuleLoader that wraps other ModuleLoader classes
       at given mount-points in the module naming space."""

    def __init__(self, sources):
        self.loaders = [AppStore.create(ms) for ms in sources]

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
            except e:
                exceptions.append(e)
        if exceptions:
            raise Exception(exceptions)

    def __repr__(self):
        return "<MultiplexedAppStore>"

    def list_apps(self):
        # List all of the apps in all of the stores.
        for ms in self.loaders:
            for app in ms.list_apps():
                yield app

class PyFsAppStore(AppStore):
    """Creates an app store from a Pyfilesystem2 filesystem, like
    a local directory containing directories for apps."""

    def __init__(self, source, fstype, fsargs):
        # Don't initialize the filesystem yet - just store the
        # class and __init__ arguments.
        self.source = source
        self.fstype = fstype
        self.fsargs = fsargs

    def __enter__(self):
        # Initialize at the start of the "with" block that this
        # object is used in.
        self.root = self.fstype(*self.fsargs)
        return self
    def __exit__(self, *args):
        # Clean up the filesystem object at the end of the "with"
        # block.
        self.root.close()

    def __repr__(self):
        if hasattr(self, 'root'):
            return "<AppStore {fs}>".format(fs=self.root)
        else:
            return "<AppStore {fstype} {fsargs}>".format(fstype=self.fstype, fsargs=self.fsargs)

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
                ret = {
                    "name": self.name,
                    "title": yaml["title"],
                }
                ret.update(yaml.get("catalog", {}))
                ret.update(self.store.get_app_catalog_info(self))
                return ret
            except ModuleDefinitionError as e:
                raise ModuleDefinitionError("There was an error loading the module at %s: %s" % (
                    err_str,
                    str(e)))
            except Exception as e:
                raise ModuleDefinitionError("There was an unhandled error loading the module at %s." % (
                    err_str,
                    str(e)))

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

                    # Load any associated Python code.
                    if (fn_name + ".py") in path_entries and self.store.source.trust_javascript_assets:
                        # Read the file.
                        with self.fs.open(fn_name + ".py") as f:
                            code = f.read()

                        # Validate that it compiles.
                        compile(code, module_id, "exec")

                        # Store it in source form in the module specification.
                        module_spec["python-module"] = code

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


class LocalDirectoryAppStore(PyFsAppStore):
    """An App Store provided by a local directory."""
    def __init__(self, source):
        from fs.osfs import OSFS
        super().__init__(source, OSFS, [source.spec["path"]])


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
        from github import Github
        g = Github(user, pw)
        self.repo = g.get_repo(repo)
        self.path = (path or "") + "/"

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


class GithubApiAppStore(PyFsAppStore):
    """An App Store provided by a local directory."""
    def __init__(self, source):
        super().__init__(source, GithubApiFilesystem, [
            source.spec["repo"], source.spec.get("path"),
            source.spec["auth"]["user"], source.spec["auth"]["pw"]])


class GitRepositoryFilesystem(SimplifiedReadonlyFilesystem):
    """
        "url": "git@github.com:GovReady/myrepository",
        "branch": "master", # optional - master is used by default
        "path": "/subpath", # this is optional, if specified it's the directory in the repo to look at
        "ssh_key": "-----BEGIN RSA PRIVATE KEY-----\nkey data\n-----END RSA PRIVATE KEY-----"
            # ^ for private repos only
    """

    def __init__(self, url, branch, path, ssh_key=None):
        self.url = url
        self.branch = branch or "master"
        self.path = (path or "") + "/"
        self.ssh_key = ssh_key

        # Create a local git working directory.
        import tempfile
        self.tempdir_obj = tempfile.TemporaryDirectory()
        self.tempdir = self.tempdir_obj.__enter__()

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

        # Fetch.
        try:
            self.repo.git.execute(
                [
                    self.repo.git.git_exec_name,
                    "fetch",
                    "--depth", "1", # avoid getting whole repo history
                    self.url, # repo URL
                    self.branch, # branch to fetch
                ], kill_after_timeout=20)
        except:
            # This is where errors occur, which is hopefully about auth.
            raise Exception("The repository URL is either not valid, not public, or ssh_key was not specified or not valid.")

        # Get the tree for the remote branch's HEAD.
        tree = self.repo.tree("FETCH_HEAD")

        # The Pythonic way would be to add a remote for the remote repository, run
        # fetch, and then access its ref.
        #self.remote = self.repo.create_remote("origin", self.spec["url"])
        #self.remote.fetch(self.spec.get("branch", "master"))
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

    def scandir(self, path, namespaces=None, page=None):
        # Get the root tree and then move to the desired subdirectory.
        from fs.info import Info
        tree = self.get_repo_root()
        for item in path.split("/"):
            if item != "":
                tree = tree[item] # TODO: As above.
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
        tree = self.get_repo_root()
        for item in path.split("/"):
            if item != "":
                tree = tree[item] # TODO: As above.
        return io.BytesIO(tree.data_stream.read())


class GitRepositoryAppStore(PyFsAppStore):
    """An App Store provided by a local directory."""
    def __init__(self, source):
        super().__init__(source, GitRepositoryFilesystem, [
            source.spec["url"], source.spec.get("branch"), source.spec.get("path"),
            source.spec.get("ssh_key")])


def read_yaml_file(f):
    # Use the safe YAML loader & catch errors.
    import yaml, yaml.scanner, yaml.parser, yaml.constructor
    try:
        return yaml.safe_load(f)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError, yaml.constructor.ConstructorError) as e:
        raise ModuleDefinitionError("There was an error parsing the YAML file: " + str(e))

AppStoreTypes = {
    "null": NullAppStore,
    "local": LocalDirectoryAppStore,
    "github": GithubApiAppStore,
    "git": GitRepositoryAppStore,
}


## LOAD MODULES ##


class ValidationError(Exception):
    def __init__(self, file_name, scope, message):
        super().__init__("There was an error in %s (%s): %s" % (file_name, scope, message))


class CyclicDependency(Exception):
    def __init__(self, path):
        super().__init__("Cyclic dependency between modules: " + " -> ".join(path + [path[0]]))


class DependencyError(Exception):
    def __init__(self, from_module, to_module):
        super().__init__("Invalid module ID %s in %s." % (to_module, from_module))


def load_module_into_database(app, module_id, available_modules, processed_modules, dependency_path, asset_pack, update_mode):
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
    # (a full path, minus .yaml) **not** including its namespace. The id is used
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
        mdb = load_module_into_database(app, m1, available_modules, processed_modules, dependency_path + [spec["id"]], asset_pack, update_mode)
        dependencies[m1] = mdb

    # Now that dependent modules are loaded, replace module string IDs with database numeric IDs.
    for q in spec.get("questions", []):
        if q.get("type") not in ("module", "module-set"): continue
        if "module-id" not in q: continue
        q["module-id"] = dependencies[q["module-id"]].id

    # Ok now actually do the database update for this module...

    # Get the most recent version of this module in the database,
    # if it exists.
    m = Module.objects.filter(source=app.store.source, key=app.store.source.namespace+"/"+app.name+"/"+spec['id'], superseded_by=None).first()
    
    if not m or update_mode == AppImportUpdateMode.New:
        # This module is new or we're asked to always create a new
        # Module instance --- create it.
        m = create_module(app, spec, asset_pack)
        processed_modules[module_id] = m
        return m

    else:
        # Has the module be changed at all? Can it be updated in place?
        change = is_module_changed(m, app.store.source, spec, asset_pack)
        
        if change is False or update_mode == AppImportUpdateMode.ForceUpdateInPlace:
            # The changes can overwrite the existing module definition
            # in the database.
            update_module(m, spec, asset_pack, True)
            processed_modules[module_id] = m
            return m

        elif change is None:
            # The module hasn't changed at all. Go on. Don't cause a
            # bump in the m.updated date.
            processed_modules[module_id] = m
            return m

        else:
            # The changes require that a new database record be created
            # to maintain data consistency. Create it, and then mark the
            # previous Module as superseded so that it is no longer used
            # on new Tasks.
            m1 = create_module(app, spec, asset_pack)
            m.visible = False
            m.superseded_by = m1
            m.save()
            processed_modules[module_id] = m1
            return m1


def get_module_spec_dependencies(spec):
    # Scans a module YAML specification for any dependencies and
    # returns a generator that yields the module IDs of the
    # dependencies.
    questions = spec.get("questions")
    if not isinstance(questions, list): questions = []
    for question in questions:
        if question.get("type") in ("module", "module-set"):
            yield question["module-id"]


def create_module(app, spec, asset_pack):
    # Create a new Module instance.
    m = Module()
    m.source = app.store.source
    m.key = app.store.source.namespace + "/" + app.name + "/" + spec['id']
    print("Creating", m.key)
    update_module(m, spec, asset_pack, False)
    return m


def remove_questions(spec):
    spec = dict(spec) # clone
    if "questions" in spec:
        del spec["questions"]
    return spec


def update_module(m, spec, asset_pack, log_status):
    # Update a module instance according to the specification data.
    # See is_module_changed.
    if log_status:
        print("Updating", repr(m))

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
            print("Deleting", repr(q))
            q.delete()


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
            if log_status: print("Updated", repr(q))
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
    #   True => Incompatible change - a new database record is needed.

    # If all other metadata is the same, then there are no changes.
    if \
            json.dumps(m.spec, sort_keys=True) == json.dumps(remove_questions(spec), sort_keys=True) \
        and m.assets == asset_pack \
        and json.dumps([q.spec for q in m.get_questions()], sort_keys=True) \
            == json.dumps([q for q in spec.get("questions", [])], sort_keys=True):
        return None

    # Define some symbols.

    compatible_change = False
    incompatible_change = True

    # Now we're just checking if the change is compatible or not with
    # the existing database record.

    if m.spec.get("version") != spec.get("version"):
        # The module writer can force a bump by changing the version
        # field.
        return incompatible_change

    # If there are no Tasks started for this Module, then the change is
    # compatible because there is no data consistency to worry about.
    if not Task.objects.filter(module=m).exists():
        return compatible_change

    # An incompatible change is the removal of a question, the change
    # of a question type, or the removal of choices from a choice
    # question --- anything that would cause a TaskQuestion/TaskAnswer
    # to have invalid data.
    qs = set()
    for definition_order, q in enumerate(spec.get("questions", [])):
        mq = ModuleQuestion.objects.filter(module=m, key=q["id"]).first()
        if not mq:
            # This is a new question. That's a compatible change.
            continue

        # Is there an incompatible change in the question? (If there
        # is a change that is compatible, we will return that the
        # module is changed anyway at the end of this method.)
        if is_question_changed(mq, definition_order, q) is True:
            return incompatible_change

        # Remember that we saw this question.
        qs.add(mq)

    # Were any questions removed?
    for q in m.questions.all():
        if q not in qs:
            return incompatible_change

    # The changes will not create any data inconsistency.
    return compatible_change

def is_question_changed(mq, definition_order, spec):
    # Returns whether a question specification has changed since
    # it was loaded into a ModuleQuestion object.
    # Returns:
    #   None => No change.
    #   False => Change, but is compatible with the database record
    #           and the database record can be updated in-place.
    #   True => Incompatible change - a new database record is needed.

    # Check if the specifications are identical. We are passed a
    # trasnformed question spec already.
    if mq.definition_order == definition_order \
        and json.dumps(mq.spec, sort_keys=True) == json.dumps(spec, sort_keys=True):
        return None

    # Change in question type -- that's incompatible.
    if mq.spec["type"] != spec["type"]:
        return True

    # Removal of a choice.
    if mq.spec["type"] in ("choice", "multiple-choice"):
        def get_choice_keys(choices): return { c.get("key") for c in choices }
        if get_choice_keys(mq.spec["choices"]) - get_choice_keys(spec["choices"]):
            return True

    # Constriction of valid number of choices to a multiple-choice
    # (min is increased or max is newly set or decreased).
    if mq.spec["type"] == "multiple-choice":
        if spec['min'] > mq.spec['min']:
            return True
        if mq.spec["max"] is None and spec["max"] is not None:
            return True
        if mq.spec["max"] is not None and spec["max"] is not None and spec["max"] < mq.spec["max"]:
            return True

    # Change in the module type if a module-type question, including
    # if the references module has been updated. spec has already
    # been transformed so that it stores an integer module database ID
    # rather than the string module ID in the YAML files.
    if mq.spec["type"] in ("module", "module-set"):
        if mq.spec["module-id"] != spec.get("module-id"):
            return True

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
    pack.paths = {
        file_path: file_hash
        for file_path, file_hash, content_loader
        in assets
    }

    # Compute the total_hash over the pack to see if this already
    # exists as a ModuleAssetPack in the database.
    pack.set_total_hash()

    existing_pack = ModuleAssetPack.objects.filter(source=source, total_hash=pack.total_hash).first()
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
            print("Storing", file_path, "with hash", file_hash)
            from django.core.files.base import ContentFile
            asset.file.save(file_path, ContentFile(content_loader()))
            asset.save()

            # Mark the asset as trusted if the source is trusted so that we can
            # serve Javascript from our domain and have it be executed by the browser.
            if source.trust_javascript_assets:
                from dbstorage.models import StoredFile
                sf = StoredFile.objects.get(path=asset.file.name)
                sf.trusted = True
                sf.save()

        # Add to the pack.
        pack.assets.add(asset)

    return pack
