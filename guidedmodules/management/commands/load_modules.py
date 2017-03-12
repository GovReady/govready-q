from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from guidedmodules.models import Module, ModuleQuestion, Task
from guidedmodules.module_logic import render_content

import sys, json

class ValidationError(Exception):
    def __init__(self, file_name, scope, message):
        super().__init__("There was an error in %s (%s): %s" % (file_name, scope, message))

class CyclicDependency(Exception):
    def __init__(self, path):
        super().__init__("Cyclic dependency between modules: " + " -> ".join(path + [path[0]]))

class DependencyError(Exception):
    def __init__(self, from_module, to_module):
        super().__init__("Invalid module ID %s in %s." % (to_module, from_module))

class ModuleRepository(object):
    @staticmethod
    def load(repo_spec):
        if repo_spec.get("type") == "local":
            return LocalModuleRepository(repo_spec)
        else:
            raise ValueError("Invalid module repository type: %s" % str(repo_spec.get("type")))

class VirtualFilesystemRepository(ModuleRepository):
    # Subclasses must define:
    #
    # listdir(path) -> iterator over tuples of ("file|dir", subpath)
    # open_file(path, mode) -> file-like object
    #
    # path is a list of path components (i.e. ["my", "directory"] for "my/directory")

    def read_yaml_file(self, path):
        # Use the safe YAML loader & catch errors.
        import yaml, yaml.scanner, yaml.parser, yaml.constructor
        with self.open_file(path, "r") as f:
            try:
                return yaml.safe_load(f)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError, yaml.constructor.ConstructorError) as e:
                raise ValidationError(repr(self) + ":" + path, "reading file", "There was an error parsing the file: " + str(e))

    def modules(self, path=[]):
        # Returns a generator that loads all modules defined in this repository.
        # Yields tuples of (module_id, module_spec).

        from os.path import splitext
        
        subdir = list(self.listdir(path))
        for ftype, fn in sorted(subdir):
            if ftype == "file":
                # If this is a file that ends in .yaml, it is a module file.
                # Strip the extension and construct a module ID that concatenates
                # the path on disk and the file name.
                fn_name, fn_ext = splitext(fn)
                if fn_ext == ".yaml":
                    # The module ID combines its local path and the filename.
                    module_id = "/".join(path + [fn_name])
                    module_spec = self.read_yaml_file(path + [fn])

                    # Load any associated Python code.
                    if ("file", fn_name + ".py") in subdir:
                        # Read the file.
                        with self.open_file(path + [fn_name + ".py"], "r") as f:
                            code = f.read()

                        # Validate that it compiles.
                        compile(code, module_id, "exec")

                        # Store it in source form in the module specification.
                        module_spec["python-module"] = code

                    yield (module_id, module_spec)

            elif fn in ("assets", "private-assets"):
                # Don't recurisvely walk into directories named 'assets' or
                # 'private-assets'. These directories provide static assets
                # that go along with the modules in that directory. 'assets'
                # are public assets that are exposed by the web server.
                pass

            elif ftype == "dir":
                # Recursively walk directories.
                for module in self.modules(path=path+[fn]):
                    yield module

    def assets(self, path=[]):
        # Returns a generator over all static assets defined in this repository.
        # Yields tuples of (path, blob) where path is the virtual path for the
        # asset and blob is binary data. Assets at e.g. modules/mygroup/assets/image.jpeg
        # are returned with the path mygroup/image.jpeg.

        import os.path # for join because we return virtual unixy paths

        # Is there an assets directory here?
        subdir = self.listdir(path)
        if ("dir", "assets") in subdir:
            for fn_type, fn in self.listdir(path + ["assets"]):
                if fn_type == "file":
                    with self.open_file(path + ["assets", fn], "rb") as f:
                        yield (os.path.join(* path+[fn]), f.read())

        # Recurse into subdirectories except ones named "assets".
        for fn_type, fn in sorted(subdir):
            if fn_type == "dir" and fn != "assets":
                for _ in self.assets(path=path+[fn]):
                    yield _

class LocalModuleRepository(VirtualFilesystemRepository):
    def __init__(self, spec):
        self.path = spec["path"]

    def listdir(self, path):
        import os, os.path
        for item in os.listdir(os.path.join(self.path, *path)):
            yield ("file" if os.path.isfile(os.path.join(*[self.path]+path+[item])) else "dir", item)

    def open_file(self, path, mode):
        import os.path
        return open(os.path.join(self.path, *path), mode)

class Command(BaseCommand):
    help = 'Updates the modules in the database using the YAML specifications in the filesystem.'
    args = '{force}'

    def handle(self, *args, **options):
        # If "force" is True, then always update
        # modules with the YAML data even if there were incompatible
        # changes. Only use this in off-line testing, since it could
        # result in an inconsistent database state with answers to
        # questions that are not valid given the question's type,
        # choices, or restrictions. And since changes in modules can
        # trigger the updating of other modules, this could have a
        # large unintended impact.
        self.force_update = False

        # Initialize all of the repositories that provide module specifications.
        repos = Command.get_module_repos()

        # Index all of the available modules.
        available_modules = { }
        for id, repo in repos.items():
            for module_path, module_spec in repo.modules():
                available_modules[id + "/" + module_path] = module_spec

        # Load modules into the database.
        self.load_modules(available_modules)

        # Build static assets directory.
        self.build_static_assets(repos)


    @staticmethod
    def get_module_repos():
        ret = {}
        for id, repo in settings.MODULE_REPOS.items():
            ret[id] = ModuleRepository.load(repo)
        return ret

    def load_modules(self, available_modules):
        # Process each module specification. Because modules may refer to
        # other modules, we also end up loading them recursively.
        ok = True
        processed_modules = set()
        for module_id in available_modules.keys():
            try:
                self.process_module(module_id, available_modules, processed_modules, [])
            except (ValidationError, CyclicDependency, DependencyError) as e:
                print(str(e))
                ok = False
        if not ok:
            print("There were some errors updating modules.")
            sys.exit(1)

        # Mark any still-visible modules that are no longer on disk as not visible.
        obsoleted_modules = Module.objects.filter(visible=True).exclude(key__in=processed_modules)
        if len(obsoleted_modules) > 0:
            print("Marking modules as obsoleted: ", obsoleted_modules)
            obsoleted_modules.update(visible=False)


    @transaction.atomic # there can be an error mid-way through updating a Module
    def process_module(self, module_id, available_modules, processed_modules, path):
        # Prevent cyclic dependencies between modules.
        if module_id in path:
            raise CyclicDependency(path)

        # Mark this YAML file as processed and skip if already processed.
        # Because of dependencies between modules, we may have already
        # been here. Do this after the cyclic dependency check or else
        # we would never see a cyclic dependency.
        if module_id in processed_modules: return
        processed_modules.add(module_id)

        # Load the module's YAML file.
        if module_id not in available_modules:
            raise DependencyError((path[-1] if len(path) > 0 else None), module_id)

        spec = available_modules[module_id]

        # Sanity check that the 'id' in the YAML file matches just the last
        # part of the path of the module_id. This allows the IDs to be 
        # relative to the path in which the module is found.
        if spec.get("id") != module_id.split('/')[-1]:
            raise ValidationError(module_id, "module", "Module 'id' field (%s) doesn't match source file path (\"%s\")." % (repr(spec.get("id")), module_id))

        # Replace spec["id"] (just the last part of the path) with the full module_id
        # (a full path, minus y.aml).
        spec["id"] = module_id

        # Recursively update any modules this module references.
        for m1 in self.get_module_spec_dependencies(spec):
            self.process_module(m1, available_modules, processed_modules, path + [spec["id"]])

        # Run some validation.

        if not isinstance(spec.get("questions"), list):
            raise ValidationError(module_id, "questions", "Invalid value for 'questions'.")

        # Pre-process the module.

        self.preprocess_module_spec(spec)

        # Ok now actually do the database update for this module...

        # Get the most recent version of this module in the database,
        # if it exists.
        m = Module.objects.filter(key=spec['id'], superseded_by=None).first()
        
        if not m:
            # This module is new --- create it.
            self.create_module(spec)

        else:
            # Has the module be chaned at all? Can it be updated in place?
            change = self.is_module_changed(m, spec)
            
            if change is None:
                # The module hasn't changed at all. Go on. Don't cause a
                # bump in the m.updated date.
                return

            elif change is False:
                # The changes can overwrite the existing module definition
                # in the database.
                self.update_module(m, spec)

            else:
                # The changes require that a new database record be created
                # to maintain data consistency. Create it, and then mark the
                # previous Module as superseded so that it is no longer used
                # on new Tasks.
                m1 = self.create_module(spec)
                m.visible = False
                m.superseded_by = m1
                m.save()


    def get_module_spec_dependencies(self, spec):
        # Scans a module YAML specification for any dependencies and
        # returns a generator that yields the module IDs of the
        # dependencies.
        questions = spec.get("questions")
        if not isinstance(questions, list): questions = []
        for question in questions:
            if question.get("type") in ("module", "module-set"):
                yield self.resolve_relative_module_id(spec, question.get("module-id"))

    def resolve_relative_module_id(self, within_module, module_id):
        # Module IDs specified in the YAML are relative to the directory in which
        # they are found. Unless they start with '/'.
        if module_id.startswith("/"):
            return module_id[1:]
        return "/".join(within_module["id"].split("/")[:-1] + [module_id])

    def preprocess_module_spec(self, spec):
        # 'introduction' fields are an alias for an interstitial
        # question that all questions depend on.
        if "introduction" in spec:
            q = {
                "id": "_introduction",
                "title": "Introduction",
                "type": "interstitial",
                "prompt": spec["introduction"]["template"],
            }
            for q1 in spec.get("questions", []):
                q1.setdefault("ask-first", []).append(q["id"])
            spec.setdefault("questions", []).insert(0, q)

    def create_module(self, spec):
        # Create a new Module instance.
        print("Creating", spec["id"])
        m = Module()
        m.key = spec['id']
        self.update_module(m, spec)
        return m


    def update_module(self, m, spec):
        # Update a module instance according to the specification data.
        # See is_module_changed.
        if m.id:
            print("Updating", repr(m))

        m.visible = True
        m.spec = self.transform_module_spec(spec)
        m.save()

        # Update its questions.
        qs = set()
        for i, question in enumerate(spec.get("questions", [])):
            qs.add(self.update_question(m, i, question))

        # Delete removed questions (only happens if the Module is
        # not yet in use).
        for q in m.questions.all():
            if q not in qs:
                print("Deleting", repr(q))
                q.delete()


    def transform_module_spec(self, spec):
        def invalid(msg):
            raise ValidationError(spec['id'], "module", msg)

        # Validate that the introduction and output documents are renderable.
        if "introduction" in spec:
            if not isinstance(spec["introduction"], dict):
                invalid("Introduction field must be a dictionary, not a %s." % str(type(spec["introduction"])))
            try:
                render_content(spec["introduction"], None, "PARSE_ONLY", "(introduction)")
            except ValueError as e:
                invalid("Introduction is an invalid Jinja2 template: " + str(e))

        if not isinstance(spec.get("output", []), list):
            invalid("Output field must be a list, not a %s." % str(type(spec.get("output"))))
        for i, doc in enumerate(spec.get("output", [])):
            try:
                render_content(doc, None, "PARSE_ONLY", "(output document)")
            except ValueError as e:
                invalid("Output document #%d is an invalid Jinja2 template: %s" % (i+1, str(e)))

        # Delete 'questions' from it because it is stored within
        # ModuleQuestion instances.
        spec = dict(spec) # clone
        if "questions" in spec:
            del spec["questions"]
        return spec


    def update_question(self, m, definition_order, spec):
        # Adds or updates a ModuleQuestion within Module m given its
        # YAML specification data in 'question'.

        # Run some transformations on the specification data first.
        spec = self.transform_question_spec(m.key, m.spec, spec)

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
            if self.is_question_changed(q, definition_order, spec) is not None:
                print("Updated", repr(q))
                for k, v in field_values.items():
                    setattr(q, k, v)
                q.save(update_fields=field_values.keys())

        return q


    def transform_question_spec(self, module_key, mspec, spec):
        if not spec.get("id"):
            raise ValidationError(mspec['id'], "questions", "Question is missing an id.")

        def invalid(msg):
            raise ValidationError(mspec['id'], "question %s" % spec['id'], msg)

        # clone dict before updating
        spec = dict(spec)

        # Perform type conversions, validation, and fill in some defaults in the YAML
        # schema so that the values are ready to use in the database.
        if spec.get("type") == "multiple-choice":
            # validate and type-convert min and max

            spec["min"] = spec.get("min", 0)
            if not isinstance(spec["min"], int) or spec["min"] < 0:
                invalid("min must be a positive integer")

            spec["max"] = None if ("max" not in spec) else spec["max"]
            if spec["max"] is not None:
                if not isinstance(spec["max"], int) or spec["max"] < 0:
                    invalid("max must be a positive integer")
        
        elif spec.get("type") in ("module", "module-set"):
            # Replace the module ID (a string) from the specification with
            # the integer ID of the module instance in the database for
            # the current Module representing that module in the filesystem.
            # Since dependencies are processed first, we know that the current
            # one in the database is the one that the YAML file meant to reference.
            try:
                spec["module-id"] = \
                    Module.objects.get(
                        key=self.resolve_relative_module_id(mspec, spec.get("module-id")),
                        superseded_by=None)\
                        .id
            except Module.DoesNotExist:
                raise DependencyError(module_key, spec.get("module-id"))
        
        elif spec.get("type") == None:
            invalid("Question is missing a type.")

        # Check that the prompt is a valid Jinja2 template.
        if spec.get("prompt") is None:
            # Prompts are optional in project modules but required elsewhere.
            if mspec.get("type") not in ("project", "system-project"):
                invalid("Question prompt is missing.")
        else:
            if not isinstance(spec.get("prompt"), str):
                invalid("Question prompt must be a string, not a %s." % str(type(spec.get("prompt"))))
            try:
                render_content({
                        "format": "markdown",
                        "template": spec["prompt"],
                    },
                    None, "PARSE_ONLY", "(question prompt)")
            except ValueError as e:
                invalid("Question prompt is an invalid Jinja2 template: " + str(e))

        # Validate impute conditions.
        imputes = spec.get("impute", [])
        if not isinstance(imputes, list):
            invalid("Impute's value must be a list.")
        for i, rule in enumerate(imputes):
            def invalid_rule(msg):
                raise ValidationError(mspec['id'], "question %s, impute condition %d" % (spec['id'], i+1), msg)

            # Check that the condition is a string, and that it's a valid Jinja2 expression.
            if not isinstance(rule.get("condition"), str):
                invalid_rule("Impute condition must be a string, not a %s." % str(type(rule["condition"])))
            from jinja2.sandbox import SandboxedEnvironment
            env = SandboxedEnvironment()
            try:
                env.compile_expression(rule["condition"])
            except Exception as e:
                invalid_rule("Impute condition %s is an invalid Jinja2 expression: %s." % (repr(rule["condition"]), str(e)))

            # Check that the value is valid. If the value-mode is raw, which
            # is the default, then any Python/YAML value is valid. We only
            # check expression values.
            if rule.get("value-mode") == "expression":
                try:
                    env.compile_expression(rule["value"])
                except Exception as e:
                    invalid_rule("Impute condition value %s is an invalid Jinja2 expression: %s." % (repr(rule["value"]), str(e)))
        
        return spec


    def is_module_changed(self, m, spec):
        # Returns whether a module specification has changed since
        # it was loaded into a Module object (and its questions).
        # Returns:
        #   None => No change.
        #   False => Change, but is compatible with the database record
        #           and the database record can be updated in-place.
        #   True => Incompatible change - a new database record is needed.
        if \
                json.dumps(m.spec, sort_keys=True) == json.dumps(self.transform_module_spec(spec), sort_keys=True) \
            and json.dumps([q.spec for q in m.get_questions()], sort_keys=True) \
                == json.dumps([self.transform_question_spec(m.key, spec, q) for q in spec.get("questions", [])], sort_keys=True):
            return None

        # Define some symbols.

        compatible_change = False
        incompatible_change = True if (not self.force_update) else False

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
            q = self.transform_question_spec(mq.module.key, spec, q)
            if self.is_question_changed(mq, definition_order, q) is True:
                return incompatible_change

            # Remember that we saw this question.
            qs.add(mq)

        # Were any questions removed?
        for q in m.questions.all():
            if q not in qs:
                return incompatible_change

        # The changes will not create any data inconsistency.
        return compatible_change

    def is_question_changed(self, mq, definition_order, spec):
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

    def build_static_assets(self, repos):
        # Store module assets into the public static directory served by the
        # web server.
        import shutil, os, os.path

        # This is the local path where static assets are stored initially
        # prior to collectstatic.
        target_root = os.path.join("siteapp", "static", "module-assets")

        # Clean out existing files.
        if os.path.exists(target_root):
            shutil.rmtree(target_root)

        # Store.
        for repo_id, repo in repos.items():
            for asset_fn, asset_blob in repo.assets():
                fn = os.path.join(target_root, repo_id, asset_fn)
                d = os.path.dirname(fn)
                os.makedirs(d, exist_ok=True)
                with open(fn, "wb") as f:
                    f.write(asset_blob)
