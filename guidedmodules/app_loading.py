###########################################################
# Import Apps into the AppVersion, Module, ModuleQuestion,
# and ModuleAsset Django ORM models.
###########################################################

import enum
import json
import logging
import structlog
import sys
from collections import OrderedDict
from structlog import get_logger

from django.db import transaction
from django.db.models.deletion import ProtectedError

from .models import AppSource, AppVersion, ModuleAsset, \
                    Module, ModuleQuestion, Task, \
                    extract_catalog_metadata

from .validate_module_specification import \
    validate_module, \
    ValidationError as ModuleValidationError

logging.basicConfig()
logger = get_logger()

class AppImportUpdateMode(enum.Enum):
    CreateInstance = 1
    ForceUpdate = 2
    CompatibleUpdate = 3

class ModuleDefinitionError(Exception):
    pass

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


@transaction.atomic # there can be an error mid-way through
def load_app_into_database(app, update_mode=AppImportUpdateMode.CreateInstance, update_appinst=None):
    # Pull in all of the modules. We need to know them all because they'll
    # be processed recursively.
    available_modules = dict(app.get_modules())

    # Create an AppVersion to add new Modules into, unless update_appinst is given.
    if update_appinst is None:
        appinst = AppVersion.objects.create(
            source=app.store.source,
            appname=app.name,
            catalog_metadata={},
            asset_paths={},
        )
    else:
        # Update Modules in this one.
        appinst = update_appinst

    # Load them all into the database. Each will trigger load_module_into_database
    # for any modules it depends on.
    processed_modules = { }
    for module_id in available_modules.keys():
        load_module_into_database(
            app,
            appinst,
            module_id,
            available_modules, processed_modules,
            [], update_mode)

    # Load assets.
    load_module_assets_into_database(app, appinst)

    # If there's an 'app' module, move the app catalog information
    # to the AppVersion.
    if 'app' in processed_modules:
        extract_catalog_metadata(processed_modules['app'])
        processed_modules['app'].save()

    # If there's a README.md file, overwrite the app catalog description.
    import re, fs.errors
    try:
        # Read the README.md.
        readme = app.read_file("README.md")

        # Strip any initial heading that has the app name itself, since
        # that is expected to not be included in the long description.
        # Check both CommonMark heading formats.
        readme = re.sub(r"^\s*#+ *" + re.escape(appinst.catalog_metadata["title"]) + r"\s*", "", readme)
        readme = re.sub(r"^\s*" + re.escape(appinst.catalog_metadata["title"]) + r"\s*[-=]+\s*", "", readme)

        appinst.catalog_metadata\
            .setdefault("description", {})["long"] = readme
    except fs.errors.ResourceNotFound:
        logger.error(event="read_from_readme.md", msg="Failed to read README.md")

    # Update appinst. It may have been modified by extract_catalog_metadata
    # and by the loading of a README.md file.
    appinst.save()

    return appinst


def load_module_into_database(app, appinst, module_id, available_modules, processed_modules, dependency_path, update_mode):
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
        spec = validate_module(spec, app)
    except ModuleValidationError as e:
        raise ValidationError(spec['id'], e.context, e.message)

    # Recursively update any modules this module references
    # because references to those modules are stored in the
    # database using a foreign key, so we need to that those
    # records in place first.
    dependencies = { }
    for m1 in get_module_spec_dependencies(spec):
        mdb = load_module_into_database(app, appinst, m1, available_modules, processed_modules, dependency_path + [spec["id"]], update_mode)
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
            logger.info(event="load_module_into_database", msg="module does not exist in database yet")
    if m:
        # What is the difference between the app's module and the module in the database?
        change = is_module_changed(m, app.store.source, spec)
    
        if change is None:
            # There is no difference, so we can go on immediately.
            pass

        elif (change is False and update_mode == AppImportUpdateMode.CompatibleUpdate) \
            or update_mode == AppImportUpdateMode.ForceUpdate:
            # There are no incompatible changes and we're allowed to update modules,
            # or we're forcing an update and it doesn't matter whether or not there
            # are changes --- update this one in place.
            update_module(m, spec, True)

        else:
            # Block an incompatible update --- don't create a new module.
            raise IncompatibleUpdate("Module {} cannot be updated because changes are incompatible with the existing data model: {}".format(module_id, change))

    if not m:
        # No Module in the database matched what we need, or an existing
        # one cannot be updated. Create one.
        m = create_module(app, appinst, spec)

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


def create_module(app, appinst, spec):
    # Create a new Module instance.
    m = Module()
    m.source = app.store.source
    m.app = appinst
    m.module_name = spec['id']
    #print("Creating", m.app, m.module_name, file=sys.stderr)
    update_module(m, spec, False)
    return m


def remove_questions(spec):
    spec = OrderedDict(spec) # clone
    if "questions" in spec:
        del spec["questions"]
    return spec


def update_module(m, spec, log_status):
    # Update a module instance according to the specification data.
    # See is_module_changed.
    if log_status:
        print("Updating", repr(m), file=sys.stderr)

    # Remove the questions from the module spec because they'll be
    # stored with the ModuleQuestion instances.
    m.visible = True
    m.spec = remove_questions(spec)
    m.save()

    # Update its questions.
    qs = set()
    for i, question in enumerate(spec.get("questions", [])):
        qs.add(update_question(m, i, question, log_status))

    # Delete removed questions (only happens if the Module is
    # not yet in use).
    for q in m.questions.all():
        if q not in qs:
            if log_status:
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

def is_module_changed(m, source, spec, module_id_map=None):
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
        and json.dumps([q.spec for q in m.get_questions()], sort_keys=True) \
            == json.dumps([q for q in spec.get("questions", [])], sort_keys=True):
        return None

    # Now we're just checking if the change is compatible or not with
    # the existing database record.

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
        qchg = is_question_changed(mq, definition_order, q, module_id_map=module_id_map)
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

    # Stop marking version changes as a blocker to upgrades
    # if m.spec.get("version") != spec.get("version"):
    #     # The module writer can force a bump by changing the version
    #     # field.
    #     return "The module version number changed, forcing a reload."

    # The changes will not create any data inconsistency.
    return False

def is_question_changed(mq, definition_order, spec, module_id_map=None):
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

    # Removal of a field in datagrid.
    if mq.spec["type"] in ("datagrid"):
        def get_field_keys(fields): return { c.get("key") for c in fields }
        rm_fields = get_field_keys(mq.spec["fields"]) - get_field_keys(spec["fields"])
        if rm_fields:
            return "One or more fields was removed: " + ", ".join(rm_fields) + "."

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

    # Constriction of valid number of rows to a datagrid
    # (min is increased or max is newly set or decreased).
    if mq.spec["type"] == "datagrid":
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
            # The ID of the module that is a valid answer for this question
            # has changed. But when upgrade an app, we expect the IDs of
            # modules defined within the app to change, so we check if
            # the ID change is expected or not. module_map, if set, has
            # a mapping of old Module instances to new Module instances
            # that will be upgraded as a part of the upgrade.
            if module_id_map is not None and module_id_map.get(mq.spec.get("module-id")) == spec.get("module-id"):
                # The module change is expected.
                pass
            else:
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

def load_module_assets_into_database(app, appinst):
    # Load all of the static assets from the source into the database.
    # If a ModuleAsset already exists for an asset, use that.

    source = app.store.source

    # Add the assets.
    appinst.trust_assets = source.trust_assets # remember setting at time of app load
    appinst.asset_paths = { }
    for file_path, file_hash, content_loader in app.get_assets():
        # Get or create the ModuleAsset --- it might already exist in an earlier app.
        asset, is_new = ModuleAsset.objects.get_or_create(
            source=source,
            content_hash=file_hash,
        )
        if is_new:
            # Set the new file content.
            from django.core.files.base import ContentFile
            asset.file.save(file_path, ContentFile(content_loader()))
            asset.save()

        mime_types = {
            "css": "text/css",
            "js": "text/javascript",
        }
        mime_type = mime_types.get(file_path.rsplit(".", 1)[-1])
        if mime_type:
            from dbstorage.models import StoredFile
            StoredFile.objects\
                .filter(path=asset.file.name)\
                .update(mime_type=mime_type)

        # Add to the app.
        appinst.asset_files.add(asset)
        appinst.asset_paths[file_path] = file_hash

    appinst.save()
