from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from guidedmodules.models import Module, ModuleQuestion, Task

import glob, os.path, yaml, json, sys

class ValidationError(Exception):
    def __init__(self, file_name, message):
        super().__init__("There was an error in %s: %s" % (file_name, message))

class CyclicDependency(Exception):
    def __init__(self, path):
        super().__init__("Cyclic dependency between modules: " + " -> ".join(path + [path[0]]))

class DependencyError(Exception):
    def __init__(self, from_module, to_module):
        super().__init__("Invalid module ID %s in %s." % (to_module, from_module))

class Command(BaseCommand):
    help = 'Upadates the modules in the database using the YAML specifications in the filesystem.'

    def handle(self, *args, **options):
        # Process each YAML file. Because YAML files may refer to
        # other YAML files, we also end up loading them recursively.
        ok = True
        processed_modules = set()
        for fn in glob.glob("modules/*.yaml"):
            module_id = os.path.splitext(os.path.basename(fn))[0]
            try:
                self.process_module(module_id, processed_modules, [])
            except (ValidationError, CyclicDependency, DependencyError) as e:
                print(str(e))
                ok = False
        if not ok:
            print("There were some errors updating modules.")
            sys.exit(1)

    @transaction.atomic # there can be an error mid-way through updating a Module
    def process_module(self, module_id, processed_modules, path):
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
        fn = os.path.join("modules", module_id + ".yaml")
        if not os.path.exists(fn):
            raise DependencyError(path[-1], module_id)
        with open(fn) as f:
            spec = yaml.load(f)
        if spec["id"] != module_id:
            raise ValidationError(fn, "Module 'id' field ('%s') doesn't match filename ('%s')." % (spec["id"], module_id))

        # Recursively update any modules this module references.
        for m1 in self.get_module_spec_dependencies(spec):
            self.process_module(m1, processed_modules, path + [spec["id"]])

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
                m.superseded_by = m1
                m.save()


    def get_module_spec_dependencies(self, spec):
        # Scans a module YAML specification for any dependencies and
        # returns a generator that yields the module IDs of the
        # dependencies.
        for question in spec.get("questions", []):
            if question.get("type") == "module":
                yield question.get("module-id")


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

        m.visible = spec.get("type") != "account"
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
        # delete 'questions' from it because it is stored within
        # ModuleQuestion instances
        spec = dict(spec) # clone
        if "questions" in spec:
            del spec["questions"]
        return spec


    def update_question(self, m, definition_order, spec):
        # Adds or updates a ModuleQuestion within Module m given its
        # YAML specification data in 'question'.

        # Run some transformations on the specification data first.
        spec = self.transform_question_spec(m, spec)

        # Create/update database record.
        q, isnew = ModuleQuestion.objects.get_or_create(
            module=m,
            key=spec["id"],
            defaults={
                "definition_order": definition_order,
                "spec": spec,
            })

        if isnew:
            print("Added", repr(q))
        else:            
            # Don't need to update the database (and we can avoid
            # bumping the .updated date) if the question's specification
            # is identifical to what's already stored.
            if self.is_question_changed(q, definition_order, spec) is not None:
                print("Updated", repr(q))
                q.definition_order = definition_order
                q.spec = spec
                q.save()

        return q


    def transform_question_spec(self, m, spec):
        spec = dict(spec) # clone
        if spec.get("type") == "multiple-choice":
            spec["min"] = int(spec.get("min", "0"))
            spec["max"] = None if ("max" not in spec) else int(spec["max"])
        elif spec.get("type") == "module":
            # Replace the module ID (a string) from the specification with
            # the integer ID of the module instance in the database for
            # the current Module representing that module in the filesystem.
            try:
                spec["module-id"] = \
                    Module.objects.get(
                        key=spec.get("module-id"),
                        superseded_by=None)\
                        .id
            except Module.DoesNotExist:
                raise DependencyError(m.key, spec.get("module-id"))
        return spec


    def is_module_changed(self, m, spec):
        # Returns whether a module specification has changed since
        # it was loaded into a Module object (and its questions).
        # Returns:
        #   None => No change.
        #   False => Change, but is compatible with the database record
        #           and the database record can be updated in-place.
        #   True => Incompatible change - a new database record is needed.

        if m.visible == (spec.get("type") != "account") \
            and json.dumps(m.spec, sort_keys=True) == json.dumps(self.transform_module_spec(spec), sort_keys=True) \
            and json.dumps([q.spec for q in m.get_questions()], sort_keys=True) \
                == json.dumps([self.transform_question_spec(m, q) for q in spec.get("questions", [])], sort_keys=True):
            return None

        # Now we're just checking if the change is compatible or not with
        # the existing database record.

        if m.spec.get("version") != spec.get("version"):
            # The module writer can force a bump by changing the version
            # field.
            return True

        # If there are no Tasks started for this Module, then the change is
        # compatible because there is no data consistency to worry about.
        if not Task.objects.filter(module=m).exists():
            return False

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
            q = self.transform_question_spec(mq, q)
            if self.is_question_changed(mq, definition_order, q) is True:
                return True

            # Remember that we saw this question.
            qs.add(mq)

        # Were any questions removed?
        for q in m.questions.all():
            if q not in qs:
                return True

        # The changes will not create any data inconsistency.
        return False

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
            def get_choice_keys(choices): return { c["key"] for c in choices }
            if get_choice_keys(mq.spec["choices"]) - get_choice_keys(spec["choices"]):
                return True

        # Constriction of valid number of choices to a multiple-choice
        # (min is increased or max is newly set or decreased).
        if mq.spec["type"] == "multiple-choice":
            if spec.get("min", 0) > mq.spec.get("min", 0):
                return True
            if "max" in spec and ("max" not in mq.spec or spec["max"] < mq.spec["max"]):
                return True

        # Change in the module type if a module-type question, including
        # if the references module has been updated. spec has already
        # been transformed so that it stores an integer module database ID
        # rather than the string module ID in the YAML files.
        if mq.spec["type"] == "module":
            if mq.spec["module-id"] != spec.get("module-id"):
                return True

        # The changes to this question do not create a data inconsistency.
        return False
