from itertools import groupby
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import PurePath
from uuid import uuid4
import rtyaml
import shutil
import operator
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, \
    HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError as SchemaValidationError
from urllib.parse import quote
from guidedmodules.models import Task, Module, AppVersion, AppSource
from siteapp.forms import ProjectForm
from siteapp.models import Project
from system_settings.models import SystemSettings
from .forms import ImportOSCALComponentForm
from .forms import StatementPoamForm, PoamForm, ElementForm
from .models import *
from .utilities import *
from simple_history.utils import update_change_reason

logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

def test(request):
    # Simple test page of routing for controls
    output = "Test works."
    html = "<html><body><p>{}</p></body></html>".format(output)
    return HttpResponse(html)

def index(request):
    """Index page for controls"""

    # Get catalog
    catalog = Catalog()
    cg_flat = catalog.get_flattened_controls_all_as_dict()
    control_groups = catalog.get_groups()
    context = {
        "catalog": catalog,
        "control": None,
        "common_controls": None,
        "control_groups": control_groups
    }
    return render(request, "controls/index.html", context)

def catalogs(request):
    """Index page for catalogs"""

    context = {
        "catalogs": Catalogs(),
        "project_form": ProjectForm(request.user),
    }
    return render(request, "controls/index-catalogs.html", context)

def catalog(request, catalog_key, system_id=None):
    """Index page for controls"""

    if system_id is None:
        system = None
    else:
        system = System.objects.get(pk=system_id)

    # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattened_controls_all_as_dict()
    control_groups = catalog.get_groups()
    context = {
        "catalog": catalog,
        "control": None,
        "common_controls": None,
        "system": system,
        "control_groups": control_groups,
        "project_form": ProjectForm(request.user),
    }
    return render(request, "controls/index.html", context)

def group(request, catalog_key, g_id):
    """Temporary index page for catalog control group"""

    # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattened_controls_all_as_dict()
    control_groups = catalog.get_groups()
    group = None
    # Get group/family of controls
    for g in control_groups:
        if g['id'].lower() == g_id:
            group = g
            break

    context = {
        "catalog": catalog,
        "control": None,
        "common_controls": None,
        "control_groups": control_groups,
        "group": group,
        "project_form": ProjectForm(request.user),
    }
    return render(request, "controls/index-group.html", context)

def control(request, catalog_key, cl_id):
    """Control detail view"""
    cl_id = oscalize_control_id(cl_id)
    catalog_key = oscalize_catalog_key(catalog_key)

    # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattened_controls_all_as_dict()

    # Handle properly formatted control id that does not exist
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", {"catalog": catalog,"control": {}})
    # Get and return the control
    context = {
        "catalog": catalog,
        "control": cg_flat[cl_id.lower()],
        "project_form": ProjectForm(request.user),
    }
    return render(request, "controls/detail.html", context)

def controls_selected(request, system_id):
    """Display System's selected controls view"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        controls = system.root_element.controls.all()
        impl_smts = system.root_element.statements_consumed.all()

        # sort controls
        controls = list(controls)
        controls.sort(key=lambda control: control.get_flattened_oscal_control_as_dict()['sort_id'])
        # controls.sort(key = lambda control:list(reversed(control.get_flattened_oscal_control_as_dict()['sort_id'])))

        impl_smts_count = {}
        ikeys = system.smts_control_implementation_as_dict.keys()
        for c in controls:
            impl_smts_count[c.oscal_ctl_id] = 0
            if c.oscal_ctl_id in ikeys:
                impl_smts_count[c.oscal_ctl_id] = len(
                    system.smts_control_implementation_as_dict[c.oscal_ctl_id]['control_impl_smts'])

        # Return the controls
        context = {
            "system": system,
            "project": project,
            "controls": controls,
            "impl_smts_count": impl_smts_count,
            "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
            "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
            "project_form": ProjectForm(request.user),
        }
        return render(request, "systems/controls_selected.html", context)
    else:
        # User does not have permission to this system
        raise Http404

def controls_updated(request, system_id):
    """Display System's statements by updated date in reverse chronological order"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        controls = system.root_element.controls.all()
        impl_smts = system.root_element.statements_consumed.all()

        impl_smts_count = {}
        ikeys = system.smts_control_implementation_as_dict.keys()
        for c in controls:
            impl_smts_count[c.oscal_ctl_id] = 0
            if c.oscal_ctl_id in ikeys:
                impl_smts_count[c.oscal_ctl_id] = len(
                    system.smts_control_implementation_as_dict[c.oscal_ctl_id]['control_impl_smts'])

        # Return the controls
        context = {
            "system": system,
            "project": project,
            "controls": controls,
            "impl_smts_count": impl_smts_count,
            "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
            "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
            "project_form": ProjectForm(request.user),
        }
        return render(request, "systems/controls_updated.html", context)
    else:
        # User does not have permission to this system
        raise Http404

def rename_element(request,element_id):
    """Update the component's name
    Args:
        request ([HttpRequest]): The network request
    component_id ([int|str]): The id of the component
    Returns:
        [JsonResponse]: Either a ok status or an error 
    """
    try:
        new_name = request.POST.get("name", "").strip() or None
        new_description = request.POST.get("description", "").strip() or None
        element = get_object_or_404(Element, id=element_id)
        element.name = new_name
        element.description = new_description
        element.save()
        logger.info(
            event="rename_element",
            element={"id": element.id, "new_name": new_name, "new_description": new_description}
        )
        return JsonResponse({ "status": "ok" }) 
    except:
        import sys
        return JsonResponse({ "status": "error", "message": sys.exc_info() })


def components_selected(request, system_id):
    """Display System's selected components view"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]

        # Return the components
        context = {
            "system": system,
            "project": project,
            "elements": Element.objects.all().exclude(element_type='system'),
            "project_form": ProjectForm(request.user),
        }
        return render(request, "systems/components_selected.html", context)
    else:
        # User does not have permission to this system
        raise Http404


def component_library(request):
    """Display the library of components"""

    context = {
        "elements": Element.objects.all().exclude(element_type='system'),
        "import_form": ImportOSCALComponentForm(),
    }

    return render(request, "components/component_library.html", context)


def import_records(request):
    """Display the records of component imports"""

    import_records = ImportRecord.objects.all()
    import_components = {}

    for import_record in import_records:
        import_components[import_record] = Element.objects.filter(import_record=import_record)

    context = {
        "import_components": import_components,
    }

    return render(request, "components/import_records.html", context)


def import_record_details(request, import_record_id):
    """Display the records of component imports"""

    import_record = ImportRecord.objects.get(id=import_record_id)
    component_statements = import_record.get_components_statements()

    context = {
        "import_record": import_record,
        "component_statements": component_statements,
    }
    return render(request, "components/import_record_details.html", context)


def confirm_import_record_delete(request, import_record_id):
    """Delete the components and statements imported from a particular import record"""

    import_record = ImportRecord.objects.get(id=import_record_id)
    component_statements = import_record.get_components_statements()
    component_count = len(component_statements)
    statement_count = 0
    for component in component_statements:
        statement_count += component_statements[component].count()

    context = {
        "import_record": import_record,
        "component_count": component_count,
        "statement_count": statement_count,
    }
    return render(request, "components/confirm_import_record_delete.html", context)


def import_record_delete(request, import_record_id):
    """Delete the components and statements imported from a particular import record"""

    import_record = ImportRecord.objects.get(id=import_record_id)
    import_created = import_record.created
    import_record.delete()

    messages.add_message(request, messages.INFO, f"Deleted import: {import_created}")

    response = redirect('/controls/components')
    return response


class ComponentSerializer(object):

    def __init__(self, element, impl_smts):
        self.element = element
        self.impl_smts = impl_smts

class OSCALComponentSerializer(ComponentSerializer):

    @staticmethod
    def statement_id_from_control(control_id, part_id):
        if part_id:
            return f"{control_id}_smt.{part_id}"
        else:
            return f"{control_id}_smt"


    def as_json(self):
        # Build OSCAL
        # Example: https://github.com/usnistgov/OSCAL/blob/master/src/content/ssp-example/json/example-component.json
        uuid = str(self.element.uuid)
        control_implementations = []
        of = {
            "component-definition": {
                "metadata": {
                    "title": "{} Component-to-Control Narratives".format(self.element.name),
                    "published": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    "last-modified": self.element.updated.replace(microsecond=0).isoformat(),
                    "version": "string",
                    "oscal-version": "1.0.0-milestone2",
                },
                "components": {
                    uuid: {
                        "name": self.element.name,
                        "component-type": self.element.element_type or "software",
                        "title": self.element.full_name or "",
                        "description": self.element.description,
                        "control-implementations": control_implementations
                    }
                }
            },
            "back-matter": []
        }

        # create requirements and organize by source (sid_class)

        by_class = defaultdict(list)
        
        # work:
        # group stmts by control-id
        # emit an requirement for the control-id
        # iterate over each group
        # emit a statement for each member of the group
        # notes:
        # - OSCAL implemented_requirements and control_implementations need UUIDs
        #   which we don't have in the db, so we construct them.

        for control_id, group in groupby(sorted(self.impl_smts, key=lambda ismt: ismt.sid),
                                         lambda ismt: ismt.sid):
            requirement = {
                "uuid": str(uuid4()),
                "control-id": control_id,
                "description": "",
                "remarks": "",
                "statements": {}
            }

            for smt in group:
                statement = {
                    "uuid": str(smt.uuid),
                    "description": smt.body,
                    "remarks": smt.remarks
                }
                statement_id = self.statement_id_from_control(control_id, smt.pid)
                requirement["statements"][statement_id] = statement
                
            by_class[smt.sid_class].append(requirement)

        for sid_class, requirements in by_class.items():
            control_implementation = {
                "uuid": str(uuid4()),
                "source": sid_class,
                "description": f"Partial implementation of {sid_class}",
                "implemented-requirements": [req for req in requirements]
            }
            control_implementations.append(control_implementation)

        oscal_string = json.dumps(of, sort_keys=False, indent=2)
        return oscal_string

class OpenControlComponentSerializer(ComponentSerializer):

    def as_yaml(self):
        ocf = {
                "name": self.element.name,
                "schema_version": "3.0.0",
                "documentation_complete": False,
                "satisfies": []
               }

        satisfies_smts = ocf["satisfies"]
        for smt in self.impl_smts:
            my_dict = {
                "control_key": smt.sid.upper(),
                "control_name": smt.catalog_control_as_dict['title'],
                "standard_key": smt.sid_class,
                "covered_by": [],
                "security_control_type": "Hybrid | Inherited | ...",
                "narrative": [
                    {"text": smt.body}
                ],
                "remarks": [
                    {"text": smt.remarks}
                ]
            }
            satisfies_smts.append(my_dict)
        opencontrol_string = rtyaml.dump(ocf)
        return opencontrol_string


class ComponentImporter(object):

    def import_components_as_json(self, import_name, json_object, request):
        """Imports Components from a JSON object

        @type import_name: str
        @param import_name: Name of import file (if it exists)
        @type json_object: dict
        @param json_object: Element attributes from JSON object
        @rtype: list if success, bool (false) if failure
        @returns: List of created components (if success) or False is failure
        """

        # Validates the format of the JSON object
        try:
            oscal_json = json.loads(json_object)
        except ValueError:
            messages.add_message(request, messages.ERROR, f"Invalid JSON. Component(s) not created.")
            return False
        if self.validate_oscal_json(oscal_json):
            # Returns list of created components
            created_components = self.create_components(oscal_json, request)
            messages.add_message(request, messages.INFO, f"Created {len(created_components)} components.")
            new_import_record = self.create_import_record(import_name, created_components)
            return new_import_record
        else:
            messages.add_message(request, messages.ERROR, f"Invalid OSCAL. Component(s) not created.")
            return False

    def create_import_record(self, import_name, components):
        """Associates components and statements to an import record

        @type import_name: str
        @param import_name: Name of import file (if it exists)
        @type components: list
        @param components: List of components
        @rtype: ImportRecord
        @returns: New ImportRecord object with components and statements associated
        """

        new_import_record = ImportRecord.objects.create(name=import_name)
        for component in components:
            statements = Statement.objects.filter(producer_element=component)
            for statement in statements:
                statement.import_record = new_import_record
                statement.save()
            component.import_record = new_import_record
            component.save()

        return new_import_record


    def validate_oscal_json(self, oscal_json):
        """Validates the JSON object is valid OSCAL format"""

        project_root = os.path.abspath(os.path.dirname(__name__))
        oscal_schema_path = os.path.join(project_root, "schemas", "oscal_component_schema.json")
        with open(oscal_schema_path, "r") as schema_content:
            oscal_json_schema = json.load(schema_content)
        try:
            validate(instance=oscal_json, schema=oscal_json_schema)
            return True
        except (SchemaError, SchemaValidationError):
            return False

    def create_components(self, oscal_json, request):
        """Creates Elements (Components) from valid OSCAL JSON"""

        components_created = []
        components = oscal_json['component-definition']['components']
        for component in components:
            new_component = self.create_component(components[component], request)
            if new_component is not None:
                components_created.append(new_component)

        return components_created

    def create_component(self, component_json, request):
        """Creates a component from a JSON dict

        @type component_json: dict
        @param component_json: Component attributes from JSON object
        @rtype: Element
        @returns: Element object if created, None otherwise
        """

        component_name = component_json['name']
        while Element.objects.filter(name=component_name).count() > 0:
            component_name = increment_element_name(component_name)

        new_component = Element.objects.create(
            name=component_name,
            description=component_json['description'] if 'description' in component_json else '',
            # Components uploaded to the Component Library are all system_element types
            # TODO: When components can be uploaded by project, set element_type from component-type OSCAL property
            element_type="system_element"
        )
        new_component.save()
        logger.info(f"Component {new_component.name} created with UUID {new_component.uuid}.")
        control_implementation_statements = component_json['control-implementations']
        for control_element in control_implementation_statements:
            catalog = oscalize_catalog_key(control_element['source']) if 'source' in control_element else None
            implemented_reqs = control_element['implemented-requirements'] if 'implemented-requirements' in control_element else []
            created_statements = self.create_control_implementation_statements(catalog, implemented_reqs,
                                                                               new_component, request)
        return new_component

    def create_control_implementation_statements(self, catalog_key, implemented_reqs, parent_component, request):
        """Creates a Statement from a JSON dictimplemented-requirements

        @type catalog_key: str
        @param catalog_key: Catalog of the control statements
        @type implemented_reqs: list
        @param implemented_reqs: Implemented controls
        @type parent_component: str
        @param parent_component: UUID of parent component
        @rtype: dict
        @returns: New statement objects created
        """

        statements_created = []

        for implemented_control in implemented_reqs:

            control_id = oscalize_control_id(implemented_control['control-id']) if 'control-id' in implemented_control else ''
            statements = implemented_control['statements'] if 'statements' in implemented_control else ''

            for stmnt_id in statements:
                statement = statements[stmnt_id]

                if self.control_exists_in_catalog(catalog_key, control_id):
                    if 'description' in statement:
                        description = statement['description']
                    elif 'description' in implemented_control:
                        description = implemented_control['description']
                    else:
                        description = ''

                    if 'remarks' in statement:
                        remarks = statement['remarks']
                    elif 'remarks' in implemented_control:
                        remarks = implemented_control['remarks']
                    else:
                        remarks = ''

                    new_statement = Statement.objects.create(
                        sid=control_id,
                        sid_class=catalog_key,
                        pid=get_control_statement_part(stmnt_id),
                        body=description,
                        statement_type="control_implementation_prototype",
                        remarks=remarks,
                        status=implemented_control['status'] if 'status' in implemented_control else None,
                        producer_element=parent_component,
                    )
                    new_statement.save()
                    logger.info(f"New statement with UUID {new_statement.uuid} created.")
                    statements_created.append(new_statement)

                else:
                    logger.info(f"Control {control_id} doesn't exist in catalog {catalog_key}. Skipping Statement...")

        return statements_created

    def control_exists_in_catalog(self, catalog_key, control_id):
        """Searches for the presence of a specific control id in a catalog.

        @type catalog_key: str
        @param catalog_key: Catalog Key
        @type control_id: str
        @param control_id: Control id
        @rtype: bool
        @returns: True if control id exists in the catalog. False otherwise
        """

        if catalog_key not in Catalogs()._list_catalog_keys():
            return False
        else:
            catalog = Catalog.GetInstance(catalog_key)
            control = catalog.get_control_by_id(control_id)
            return True if control is not None else False


def system_element(request, system_id, element_id):
    """Display System's selected element detail view"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]

        # Retrieve element
        element = Element.objects.get(id=element_id)

        # Retrieve impl_smts produced by element and consumed by system
        # Get the impl_smts contributed by this component to system
        impl_smts = element.statements_produced.filter(consumer_element=system.root_element)

        # Retrieve used catalog_key
        catalog_key = impl_smts[0].sid_class

        # Retrieve control ids
        catalog_controls = Catalog.GetInstance(catalog_key=catalog_key).get_controls_all()

        # Build OSCAL and OpenControl
        oscal_string = OSCALComponentSerializer(element, impl_smts).as_json()
        opencontrol_string = OpenControlComponentSerializer(element, impl_smts).as_yaml()

        # Return the system's element information
        context = {
            "system": system,
            "project": project,
            "element": element,
            "impl_smts": impl_smts,
            "catalog_controls": catalog_controls,
            "catalog_key": catalog_key,
            "oscal": oscal_string,
            "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
            "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
            "opencontrol": opencontrol_string,
            "project_form": ProjectForm(request.user),
        }
        return render(request, "systems/element_detail_tabs.html", context)

@login_required
def new_element(request):
    """Form to create new system element (aka component)"""

    if request.method == 'POST':
        form = ElementForm(request.POST)
        if form.is_valid():
            form.save()
            element = form.instance
            logger.info(
                event="new_element",
                object={"object": "element", "id": element.id, "name":element.name},
                user={"id": request.user.id, "username": request.user.username}
            )
            return redirect('component_library_component', element_id=element.id)
    else:
        form = ElementForm()

    return render(request, 'components/element_form.html', {
        'form': form,
    })

def component_library_component(request, element_id):
    """Display certified component's element detail view"""

    # Retrieve element
    element = Element.objects.get(id=element_id)

    # Retrieve impl_smts produced by element and consumed by system
    # Get the impl_smts contributed by this component to system
    impl_smts = element.statements_produced.filter(statement_type="control_implementation_prototype")
    
    if len(impl_smts) < 1:
        context = {
            "element": element,
            "impl_smts": impl_smts,
            "is_admin": request.user.is_superuser,
            "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
            "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
        }
        return render(request, "components/element_detail_tabs.html", context)

    if len(impl_smts) == 0:
        # New component, no control statements assigned yet
        catalog_key = "catalog_key_missing"
        catalog_controls = None
        oscal_string = None
        opencontrol_string = None
    elif len(impl_smts) > 0:
        # TODO: We may have multiple catalogs in this case in the future
        # Retrieve used catalog_key
        catalog_key = impl_smts[0].sid_class
        # Retrieve control ids
        catalog_controls = Catalog.GetInstance(catalog_key=catalog_key).get_controls_all()
        # Build OSCAL and OpenControl
        oscal_string = OSCALComponentSerializer(element, impl_smts).as_json()
        opencontrol_string = OpenControlComponentSerializer(element, impl_smts).as_yaml()

    # Return the system's element information
    context = {
        "element": element,
        "impl_smts": impl_smts,
        "catalog_controls": catalog_controls,
        "catalog_key": catalog_key,
        "oscal": oscal_string,
        "is_admin": request.user.is_superuser,
        "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
        "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
        "opencontrol": opencontrol_string,
        # "project_form": ProjectForm(request.user),
    }
    return render(request, "components/element_detail_tabs.html", context)

def api_controls_select(request):
    """Return list of controls in json for select2 options from all control catalogs"""

    # Create array to hold accumulated controls
    cxs = []
    # Loop through control catalogs
    catalogs = Catalogs()
    for ck in catalogs._list_catalog_keys():
        cx = Catalog.GetInstance(catalog_key=ck)
        # Get controls
        ctl_list = cx.get_flattened_controls_all_as_dict()
        # Build objects for rendering Select2 auto complete list from catalog
        select_list = [{'id': ctl_list[ctl]['id'], 'title': ctl_list[ctl]['title'], 'class': ctl_list[ctl]['class'], 'catalog_key_display': cx.catalog_key_display, 'display_text': f"{ctl_list[ctl]['label']} - {ctl_list[ctl]['title']} - {cx.catalog_key_display}"} for ctl in ctl_list]
        # Extend array of accumuated controls with catalog's control list
        cxs.extend(select_list)
    # Sort the accummulated list
    cxs.sort(key = operator.itemgetter('id', 'catalog_key_display'))
    data = cxs

    if True:
        status = "ok"
        message = "Sending list."
        return JsonResponse( {"status": "success", "message": message, "data": {"controls": data} })
    else:
        status = "error"
        message = "Could not generate controls list."
        data = {}
        return JsonResponse({"status": status, "message": message, "data": data})

def component_library_component_copy(request, element_id):
    """Copy a component"""

    # Retrieve element
    element = Element.objects.get(id=element_id)

    e_copy = element.copy()

    # Create message to display to user
    messages.add_message(request, messages.INFO,
                         'Component "{}" copied to "{}".'.format(element.name, e_copy.name))

    # Redirect to the new page for the component
    return HttpResponseRedirect("/controls/components/{}".format(e_copy.id))


@login_required
def import_component(request):
    """Import a Component in JSON"""

    import_name = request.POST.get('import_name', '')
    oscal_component_json = request.POST.get('json_content', '')
    result = ComponentImporter().import_components_as_json(import_name, oscal_component_json, request)
    return component_library(request)

def statement_history(request, smt_id=None):
    """Returns the history for the given statement"""
    from controls.models import Statement
    full_smt_history = None
    try:
        smt = Statement.objects.get(id=smt_id)
        full_smt_history = smt.history.all()
    except Statement.DoesNotExist:
        messages.add_message(request, messages.ERROR, f'The statement id is not valid. Is this still a statement in GovReady?')

    context = {"statement": full_smt_history}

    return render(request, "controls/statement_history.html", context)

def restore_to_history(request, smt_id, history_id):
    """
    Restore the current model instance to a previous version
    """
    full_smt_history = None
    for query_key in request.POST:
        if "restore" in query_key:
            change_reason = request.POST.get(query_key, "")
        else:
            change_reason = None
    try:
        smt = Statement.objects.get(id=smt_id)
        recent_smt = smt.history.first()

    except ObjectDoesNotExist as ex:
        messages.add_message(request, messages.ERROR, f'{ex} The statement id is not valid. Is this still a statement in GovReady?')

    try:
        historical_smt = smt.history.get(history_id=history_id)
        # saving historical statement as a new instance
        historical_smt.instance.save()
        # Update the reason for the new statement record
        update_change_reason(smt.history.first().instance, change_reason)

        logger.info( f"Change reason: {change_reason}")

        logger.info(
            f"Restoring the current statement with an id of {smt_id} to version with a history id of {history_id}")
        messages.add_message(request, messages.INFO,
                             f'Successfully restored the statement to version history {history_id}')

        # Diff between most recent and the historical record
        full_smt_history = smt.history.all()
        recent_record = full_smt_history.filter(history_id=recent_smt.history_id).first()
        historical_record = full_smt_history.filter(history_id=historical_smt.history_id).first()

        delta = historical_record.diff_against(recent_record)
        for change in delta.changes:
            logger.info("{} changed from {} to {}".format(change.field, change.old, change.new))
    except ObjectDoesNotExist as ex:
        messages.add_message(request, messages.ERROR, f'{ex} Is this still a statement record in GovReady?')

    context = {
        "history_id": history_id,
        "smt_id": smt_id,
        "statement": full_smt_history}

    return render(request, "controls/statement_history.html", context)

def system_element_download_oscal_json(request, system_id, element_id):

    if system_id is not None and system_id != '':
        # Retrieve identified System
        system = System.objects.get(id=system_id)
        # Retrieve related selected controls if user has permission on system
        if request.user.has_perm('view_system', system):
            # Retrieve primary system Project
            # Temporarily assume only one project and get first project
            project = system.projects.all()[0]

            # Retrieve element
            element = Element.objects.get(id=element_id)

            # Retrieve impl_smts produced by element and consumed by system
            # Get the impl_smts contributed by this component to system
            impl_smts = element.statements_produced.filter(consumer_element=system.root_element)
    else:
        # Comes from Component Library, no system

        # Retrieve element
        element = Element.objects.get(id=element_id)
        # Get the impl_smts contributed by this component to system
        impl_smts = Statement.objects.filter(producer_element=element)

    response = HttpResponse(content_type="application/json")
    filename = str(PurePath(slugify(element.name)).with_suffix('.json'))
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    body = OSCALComponentSerializer(element, impl_smts).as_json()
    response.write(body)

    return response


def controls_selected_export_xacta_xslx(request, system_id):
    """Export System's selected controls compatible with Xacta 360"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        controls = system.root_element.controls.all()

        # Retrieve any related Implementation Statements
        impl_smts = system.root_element.statements_consumed.all()
        impl_smts_by_sid = {}
        for smt in impl_smts:
            if smt.sid in impl_smts_by_sid:
                impl_smts_by_sid[smt.sid].append(smt)
            else:
                impl_smts_by_sid[smt.sid] = [smt]

        for control in controls:
            if control.oscal_ctl_id in impl_smts_by_sid:
                setattr(control, 'impl_smts', impl_smts_by_sid[control.oscal_ctl_id])
            else:
                setattr(control, 'impl_smts', None)

        from openpyxl import Workbook
        from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment
        from tempfile import NamedTemporaryFile

        wb = Workbook()
        ws = wb.active
        # create alignment style
        wrap_alignment = Alignment(wrap_text=True)
        ws.title = "Controls_Implementation"

        # Add in field name row
        # Paragraph/ReqID
        c = ws.cell(row=1, column=1, value="Paragraph/ReqID")
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(left=Side(border_style="thin", color="444444"), right=Side(border_style="thin", color="444444"),
                          bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Stated Requirement (Control statement/Requirement)
        c = ws.cell(row=1, column=2, value="Title")
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        ws.column_dimensions['B'].width = 30
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Private Implementation
        c = ws.cell(row=1, column=3, value="Private Implementation")
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        ws.column_dimensions['C'].width = 80
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Public Implementation
        c = ws.cell(row=1, column=4, value="Public Implementation")
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        ws.column_dimensions['D'].width = 80
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Notes
        c = ws.cell(row=1, column=5, value="Notes")
        ws.column_dimensions['E'].width = 60
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Status ["Implemented", "Planned"]
        c = ws.cell(row=1, column=6, value="Status")
        ws.column_dimensions['F'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Expected Completion (expected implementation)
        c = ws.cell(row=1, column=7, value="Expected Completion")
        ws.column_dimensions['G'].width = 20
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Class ["Management", "Operational", "Technical",
        c = ws.cell(row=1, column=8, value="Class")
        ws.column_dimensions['H'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Priority ["p0", "P1", "P2", "P3"]
        c = ws.cell(row=1, column=9, value="Priority")
        ws.column_dimensions['I'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Responsible Entities
        c = ws.cell(row=1, column=10, value="Responsible Entities")
        ws.column_dimensions['J'].width = 20
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Control Owner(s)
        c = ws.cell(row=1, column=11, value="Control Owner(s)")
        ws.column_dimensions['K'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Type ["System-Specific", "Hybrid", "Inherited", "Common", "blank"]
        c = ws.cell(row=1, column=12, value="Type")
        ws.column_dimensions['L'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Inherited From
        c = ws.cell(row=1, column=13, value="Inherited From")
        ws.column_dimensions['M'].width = 20
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Provide As ["Do Not Share", "blank"]
        c = ws.cell(row=1, column=14, value="Provide As")
        ws.column_dimensions['N'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Evaluation Status ["Evaluated", "Expired", "Not Evaluated", "Unknown", "blank"]
        c = ws.cell(row=1, column=15, value="Evaluation Status")
        ws.column_dimensions['O'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # Control Origination
        c = ws.cell(row=1, column=16, value="Control Origination")
        ws.column_dimensions['P'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        # History
        c = ws.cell(row=1, column=17, value="History")
        ws.column_dimensions['Q'].width = 15
        c.fill = PatternFill("solid", fgColor="5599FE")
        c.font = Font(color="FFFFFF", bold=True)
        c.border = Border(right=Side(border_style="thin", color="444444"), bottom=Side(border_style="thin", color="444444"),
                          outline=Side(border_style="thin", color="444444"))

        for row in range(2, len(controls) + 1):
            control = controls[row - 2]

            # Paragraph/ReqID
            c = ws.cell(row=row, column=1, value=control.get_flattened_oscal_control_as_dict()['id_display'].upper())
            c.fill = PatternFill("solid", fgColor="FFFF99")
            c.alignment = Alignment(vertical='top', wrapText=True)
            c.border = Border(left=Side(border_style="thin", color="444444"),
                              right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Title
            c = ws.cell(row=row, column=2, value=control.get_flattened_oscal_control_as_dict()['title'])
            c.fill = PatternFill("solid", fgColor="FFFF99")
            c.alignment = Alignment(vertical='top', wrapText=True)
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Private Implementation
            smt_combined = ""
            if control.impl_smts:
                for smt in control.impl_smts:
                    smt_combined += smt.body
            c = ws.cell(row=row, column=3, value=smt_combined)
            c.alignment = Alignment(vertical='top', wrapText=True)
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Public Implementation
            c.alignment = Alignment(vertical='top', wrapText=True)
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Notes
            c = ws.cell(row=1, column=5, value="Notes")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Status ["Implemented", "Planned"]
            c = ws.cell(row=1, column=6, value="Status")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Expected Completion (expected implementation)
            c = ws.cell(row=1, column=7, value="Expected Completion")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Class ["Management", "Operational", "Technical",
            c = ws.cell(row=1, column=8, value="Class")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Priority ["p0", "P1", "P2", "P3"]
            c = ws.cell(row=1, column=9, value="Priority")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Responsible Entities
            c = ws.cell(row=1, column=10, value="Responsible Entities")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Control Owner(s)
            c = ws.cell(row=1, column=11, value="Control Owner(s)")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Type ["System-Specific", "Hybrid", "Inherited", "Common", "blank"]
            c = ws.cell(row=1, column=12, value="Type")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Inherited From
            c = ws.cell(row=1, column=13, value="Inherited From")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Provide As ["Do Not Share", "blank"]
            c = ws.cell(row=1, column=14, value="Provide As")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Evaluation Status ["Evaluated", "Expired", "Not Evaluated", "Unknown", "blank"]
            c = ws.cell(row=1, column=15, value="Evaluation Status")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # Control Origination
            c = ws.cell(row=1, column=16, value="Control Origination")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

            # History
            c = ws.cell(row=1, column=17, value="History")
            c.border = Border(right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()
            blob = stream

        mime_type = "application/octet-stream"
        filename = "{}_control_implementations-{}.xlsx".format(system.root_element.name.replace(" ", "_"),
                                                               datetime.now().strftime("%Y-%m-%d-%H-%M"))

        resp = HttpResponse(blob, mime_type)
        resp['Content-Disposition'] = 'inline; filename=' + filename
        return resp
    else:
        # User does not have permission to this system
        raise Http404


def editor(request, system_id, catalog_key, cl_id):
    """System Control detail view"""

    cl_id = oscalize_control_id(cl_id)
    catalog_key = oscalize_catalog_key(catalog_key)

    # Get control catalog
    catalog = Catalog(catalog_key)

    # TODO: maybe catalogs could provide an API that returns a set of 
    # control ids instead?

    cg_flat = catalog.get_flattened_controls_all_as_dict()

    # If control id does not exist in catalog
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", {"catalog": catalog,"control": {}})

    # Retrieve identified System
    system = System.objects.get(id=system_id)

    # Retrieve related statements if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        # if len(projects) > 0:
        #     project = projects[0]
        # Retrieve any related CommonControls
        # CRITICAL TODO: Filter by sid and by system.root_element

        # Retrieve organizational parameter settings for this catalog
        # We need to grab the catalog again.

        parameter_values = project.get_parameter_values(catalog_key)
        catalog = Catalog(catalog_key, parameter_values=parameter_values)
        cg_flat = catalog.get_flattened_controls_all_as_dict()

        common_controls = CommonControl.objects.filter(oscal_ctl_id=cl_id)
        ccp_name = None
        if common_controls:
            cc = common_controls[0]
            ccp_name = cc.common_control_provider.name
        # Get and return the control

        # Retrieve any related Implementation Statements filtering by control and system.root_element
        impl_smts = Statement.objects.filter(sid=cl_id, consumer_element=system.root_element).order_by('pid')

        # Build OSCAL
        # Example: https://github.com/usnistgov/OSCAL/blob/master/content/ssp-example/json/ssp-example.json
        of = {
            "system-security-plan": {
                "id": "example-ssp",
                "metadata": {
                    "title": "{} System Security Plan Excerpt".format(system.root_element.name),
                    "published": datetime.now().replace(microsecond=0).isoformat(),
                    "last-modified": "element.updated.replace(microsecond=0).isoformat()",
                    "version": "1.0",
                    "oscal-version": "1.0.0-milestone3",
                    "roles": [],
                    "parties": [],
                },
                "import-profile": {},
                "system-characteristics": {},
                "system-implementations": {},
                "control-implementation": {
                    "description": "",
                    "implemented-requirements": {
                        "control-id": "{}".format(cl_id),
                        "description": "",
                        "statements": {
                            "{}_smt".format(cl_id): {
                                "description": "N/A",
                                "by-components": {
                                }
                            }
                        }  #statements
                    },  # implemented-requirements
                },
                "back-matter": []
            }
        }
        by_components = of["system-security-plan"]["control-implementation"]["implemented-requirements"]["statements"][
            "{}_smt".format(cl_id)]["by-components"]
        for smt in impl_smts:
            my_dict = {
                smt.sid + "{}".format(smt.producer_element.name.replace(" ", "-")): {
                    "description": smt.body,
                    "role-ids": "",
                    "set-params": {},
                    "remarks": smt.remarks
                },
            }
            by_components.update(my_dict)
        oscal_string = json.dumps(of, sort_keys=False, indent=2)

        # Build combined statement if it exists
        if cl_id in system.control_implementation_as_dict:
            combined_smt = system.control_implementation_as_dict[cl_id]['combined_smt']
        else:
            combined_smt = ""

        # Define status options
        impl_statuses = ["Not implemented", "Planned", "Partially implemented", "Implemented", "Unknown"]

      # Only elements for the given control id, sid, and statement type

        elements =  Element.objects.all().exclude(element_type='system')

        context = {
            "system": system,
            "project": project,
            "catalog": catalog,
            "control": cg_flat[cl_id.lower()],
            "common_controls": common_controls,
            "ccp_name": ccp_name,
            "impl_smts": impl_smts,
            "impl_statuses": impl_statuses,
            "combined_smt": combined_smt,
            "oscal": oscal_string,
            "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
            "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
            "opencontrol": "opencontrol_string",
            "project_form": ProjectForm(request.user),
            "elements": elements,
        }
        return render(request, "controls/editor.html", context)
    else:
        # User does not have permission to this system
        raise Http404

def editor_compare(request, system_id, catalog_key, cl_id):
    """System Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get control catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattened_controls_all_as_dict()
    # If control id does not exist in catalog
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", {"catalog": catalog,"control": {}})

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related statements if owner has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        # Retrieve any related CommonControls
        common_controls = CommonControl.objects.filter(oscal_ctl_id=cl_id)
        ccp_name = None
        if common_controls:
            cc = common_controls[0]
            ccp_name = cc.common_control_provider.name
        # Get and return the control

        # Retrieve any related Implementation Statements
        impl_smts = Statement.objects.filter(sid=cl_id)
        context = {
            "system": system,
            "project": project,
            "catalog": catalog,
            "control": cg_flat[cl_id.lower()],
            "common_controls": common_controls,
            "ccp_name": ccp_name,
            "impl_smts": impl_smts,
            "project_form": ProjectForm(request.user),
        }
        return render(request, "controls/compare.html", context)
    else:
        # User does not have permission to this system
        raise Http404


# @task_view
def save_smt(request):
    """Save a statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
        # EXAMPLE CODE FOR GUARDIAN PERMISSIONS
        # does user have write privs?
        # if not task.has_write_priv(request.user):
        #     return HttpResponseForbidden()

        # validate question
        # q = task.module.questions.get(id=request.POST.get("question"))

        # validate and parse value
        # if request.POST.get("method") == "clear":
        #     # Clear means that the question returns to an unanswered state.
        #     # This method is only offered during debugging to make it easier
        #     # to test the application's behavior when questions are unanswered.
        #     value = None
        #     cleared = True
        #     skipped_reason = None
        #     unsure = False

        # elif request.POST.get("method") == "skip":
        #     # The question is being skipped, i.e. answered with a null value,
        #     # because the user doesn't know the answer, it doesn't apply to
        #     # the user's circumstances, or they want to return to it later.
        #     value = None
        #     cleared = False
        #     skipped_reason = request.POST.get("skipped_reason") or None
        #     unsure = bool(request.POST.get("unsure"))

        # Track if we are creating a new statement
        new_statement = False
        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]
        # Updating or saving a new statement?
        if len(form_values['smt_id']) > 0:
            # Look up existing Statement object
            statement = Statement.objects.get(pk=form_values['smt_id'])

            # Check user permissions
            system = statement.consumer_element
            if not request.user.has_perm('change_system', system):
                # User does not have write permissions
                # Log permission to save answer denied
                logger.info(
                    event="save_smt permission_denied",
                    object={"object": "statement", "id": statement.id},
                    user={"id": request.user.id, "username": request.user.username}
                )
                return HttpResponseForbidden(
                    "Permission denied. {} does not have change privileges to system and/or project.".format(
                        request.user.username))

            if statement is None:
                # Statement from received has an id no longer in the database.
                # Report error. Alternatively, in future save as new Statement object
                statement_status = "error"
                statement_msg = "The id for this statement is no longer valid in the database."
                return JsonResponse({"status": "error", "message": statement_msg})
            # Update existing Statement object with received info
            statement.pid = form_values['pid']
            statement.body = form_values['body']
            statement.remarks = form_values['remarks']
            statement.status = form_values['status']
        else:
            # Create new Statement object
            statement = Statement(
                sid=oscalize_control_id(form_values['sid']),
                sid_class=form_values['sid_class'],
                body=form_values['body'],
                pid=form_values['pid'],
                statement_type=form_values['statement_type'],
                status=form_values['status'],
                remarks=form_values['remarks'],
            )
            new_statement = True
            # Convert the human readable catalog name to proper catalog key, if needed
            # from huma readable `NIST SP-800-53 rev4` to `NIST_SP-800-53_rev4`
            statement.sid_class = statement.sid_class.replace(" ","_")

        # Save Statement object
        try:
            statement.save()
            statement_status = "ok"
            statement_msg = "Statement saved."
        except Exception as e:
            statement_status = "error"
            statement_msg = "Statement save failed. Error reported {}".format(e)
            return JsonResponse({"status": "error", "message": statement_msg})

        # Updating or saving a new producer_element?
        try:
            # Does the name match and existing element? (Element names are unique.)
            # TODO: Sanitize data entered in form?
            producer_element, created = Element.objects.get_or_create(name=form_values['producer_element_name'])
            if created:
                producer_element.element_type = "system_element"
                producer_element.save()
            producer_element_status = "ok"
            producer_element_msg = "Producer Element saved."
        except Exception as e:
            producer_element_status = "error"
            producer_element_msg = "Producer Element save failed. Error reported {}".format(e)
            return JsonResponse({"status": "error", "message": producer_element_msg})

        # Associate Statement and Producer Element if creating new statement
        if new_statement:
            try:
                statement.producer_element = producer_element
                statement.save()
                statement_element_status = "ok"
                statement_element_msg = "Statement associated with Producer Element."
            except Exception as e:
                statement_element_status = "error"
                statement_element_msg = "Failed to associate statement with Producer Element {}".format(e)
                return JsonResponse(
                    {"status": "error", "message": statement_msg + " " + producer_element_msg + " " + statement_element_msg})

        # Create new Prototype Statement object on new statement creation (not statement edit)
        if new_statement:
            try:
                statement_prototype = statement.create_prototype()
            except Exception as e:
                statement_status = "error"
                statement_msg = "Statement save failed while saving statement prototype. Error reported {}".format(e)
                return JsonResponse({"status": "error", "message": statement_msg})

        # Retain only prototype statement if statement is created in the component library
        # A statement of type `control_implementation` should only exists if associated a consumer_element.
        # When the statement is created in the component library, no consuming_element will exist.
        # TODO
        # - Delete the statement that created the statement prototyp
        # - Skip the associating the statement with the system's root_element because we do not have a system identified
        statement_del_msg = ""
        if "form_source" in form_values and form_values['form_source'] == 'component_library':
            # Form source is part of form
            # Form received from component library
            from django.core import serializers
            serialized_obj = serializers.serialize('json', [statement, ])
            # Delete statement
            statement.delete()
            statement_del_msg = "Statement unassociated with System/Consumer Element deleted."
        else:
            # Associate Statement and System's root_element
            system_id = form_values['system_id']
            if new_statement and system_id is not None:
                try:
                    statement.consumer_element = System.objects.get(pk=form_values['system_id']).root_element
                    statement.save()
                    statement_consumer_status = "ok"
                    statement_consumer_msg = "Statement associated with System/Consumer Element."
                except Exception as e:
                    statement_consumer_status = "error"
                    statement_consumer_msg = "Failed to associate statement with System/Consumer Element {}".format(e)
                    return JsonResponse(
                        {"status": "error", "message": statement_msg + " " + producer_element_msg + " " + statement_consumer_msg})

            # If we are updating a smt of type control_implementation_prototype from a system
            # then update ElementControl smts_updated to know when control element on system was recently updated
            statement_element_msg = ""
            if statement.statement_type == "control_implementation":
                try:
                    ec = ElementControl.objects.get(element=statement.consumer_element, oscal_ctl_id=statement.sid,
                                                    oscal_catalog_key=statement.sid_class)
                    ec.smts_updated = statement.updated
                    ec.save()
                except Exception as e:
                    statement_element_status = "error"
                    statement_element_msg = "Failed to update ControlElement smt_updated {}".format(e)
                    return JsonResponse(
                        {"status": "error", "message": statement_msg + " " + producer_element_msg + " " + statement_element_msg})

            # Serialize saved data object(s) to send back to update web page
            # The submitted form needs to be updated with the object primary keys (ids)
            # in order that future saves will be treated as updates.
            from django.core import serializers
            serialized_obj = serializers.serialize('json', [statement, ])

    # Return successful save result to web page's Ajax request
    return JsonResponse(
        {"status": "success", "message": statement_msg + " " + producer_element_msg + " " + statement_element_msg + statement_del_msg,
         "statement": serialized_obj})

def update_smt_prototype(request):
    """Update a certified statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]

        statement = Statement.objects.get(pk=form_values['smt_id'])
        system = statement.consumer_element

        # Test if user is admin
        if not request.user.is_superuser:
            # User is not Admin and does not have permission to update statement prototype
            # Log permission update statement prototype answer denied
            logger.info(
                event="update_smt_permission permission_denied",
                object={"object": "statement", "id": statement.id},
                user={"id": request.user.id, "username": request.user.username}
            )
            return HttpResponseForbidden("Permission denied. {} does not have change privileges to update statement prototype.".format(request.user.username))

        if statement is None:
            statement_status = "error"
            statement_msg = "The id for this statement is no longer valid in the database."
            return JsonResponse({ "status": "error", "message": statement_msg })

        # needs self.body == self.prototype.body

        try:
            proto_statement = Statement.objects.get(pk=statement.prototype_id)
            proto_statement.prototype.body = statement.body
            proto_statement.prototype.save()
            statement_status = "ok"
            statement_msg = f"Update to statement prototype {proto_statement.prototype_id} succeeded."
        except Exception as e:
            statement_status = "error"
            statement_msg = "Update to statement prototype failed. Error reported {}".format(e)
            return JsonResponse({ "status": "error", "message": statement_msg })

        return JsonResponse({ "status": "success", "message": statement_msg, "data": { "smt_body": statement.body } })

def delete_smt(request):
    """Delete a statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
        # check permissions
        # EXAMPLE CODE FOR GUARDIAN PERMISSIONS
        # # does user have write privs?
        # # if not task.has_write_priv(request.user):
        # #     return HttpResponseForbidden()

        # # validate question
        # # q = task.module.questions.get(id=request.POST.get("question"))

        # # validate and parse value
        # # if request.POST.get("method") == "clear":
        # #     # Clear means that the question returns to an unanswered state.
        # #     # This method is only offered during debugging to make it easier
        # #     # to test the application's behavior when questions are unanswered.
        # #     value = None
        # #     cleared = True
        # #     skipped_reason = None
        # #     unsure = False

        # # elif request.POST.get("method") == "skip":
        # #     # The question is being skipped, i.e. answered with a null value,
        # #     # because the user doesn't know the answer, it doesn't apply to
        # #     # the user's circumstances, or they want to return to it later.
        # #     value = None
        # #     cleared = False
        # #     skipped_reason = request.POST.get("skipped_reason") or None
        #     unsure = bool(request.POST.get("unsure"))

        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]

        # Delete statement?
        statement = Statement.objects.get(pk=form_values['smt_id'])

        # Check user permissions
        system = statement.consumer_element
        if not request.user.has_perm('change_system', system):
            # User does not have write permissions
            # Log permission to save answer denied
            logger.info(
                event="delete_smt permission_denied",
                object={"object": "statement", "id": statement.id},
                user={"id": request.user.id, "username": request.user.username}
            )
            return HttpResponseForbidden(
                "Permission denied. {} does not have change privileges to system and/or project.".format(
                    request.user.username))

        if statement is None:
            # Statement from received has an id no longer in the database.
            # Report error. Alternatively, in future save as new Statement object
            statement_status = "error"
            statement_msg = "The id for this statement is no longer valid in the database."
            return JsonResponse({ "status": "error", "message": statement_msg })
        # Delete Statement object
        try:
            statement.delete()
            statement_status = "ok"
            statement_msg = "Statement deleted."
        except Exception as e:
            statement_status = "error"
            statement_msg = "Statement delete failed. Error reported {}".format(e)
            return JsonResponse({"status": "error", "message": statement_msg})

        # TODO Record fact statement deleted
        # Below will not work because statement is deleted
        # and need to show in racird that a statement was recently deleted
        # Update ElementControl smts_updated to know when control element on system was recently updated
        # try:
        #     print("Updating ElementControl smts_updated")
        #     ec = ElementControl.objects.get(element=statement.consumer_element, oscal_ctl_id=statement.sid, oscal_catalog_key=statement.sid_class)
        #     ec.smts_updated = statement.updated
        #     ec.save()
        # except Exception as e:
        #     statement_element_status = "error"
        #     statement_element_msg = "Failed to update ControlElement smt_updated {}".format(e)
        #     return JsonResponse({ "status": "error", "message": statement_msg + " " + producer_element_msg + " " +statement_element_msg })

        return JsonResponse({"status": "success", "message": statement_msg})


# Components

def add_system_component(request, system_id):
    """Add an existing element and its statements to a system"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form_dict = dict(request.POST)
    form_values = {}
    for key in form_dict.keys():
        form_values[key] = form_dict[key][0]

    # Does user have permission to add element?
    # Check user permissions
    system = System.objects.get(pk=system_id)
    if not request.user.has_perm('change_system', system):
        # User does not have write permissions
        # Log permission to save answer denied
        logger.info(
            event="change_system permission_denied",
            object={"object": "element", "producer_element_name": form_values['producer_element_name']},
            user={"id": request.user.id, "username": request.user.username}
        )
        return HttpResponseForbidden("Permission denied. {} does not have change privileges to system and/or project.".format(request.user.username))

    # DEBUG
    # print(f"Atempting to add {producer_element.name} (id:{producer_element.id}) to system_id {system_id}")

    # Get system's existing components selected
    elements_selected = system.producer_elements
    elements_selected_ids = [e.id for e in elements_selected]

    # Get system's selected controls because we only want to add statements for selected controls
    selected_controls = system.root_element.controls.all()
    selected_controls_ids = set([f"{sc.oscal_ctl_id} {sc.oscal_catalog_key}" for sc in selected_controls])
    # TODO: Refactor above line selected_controls into a system model function if not already existing

    # Add element to system's selected components
    # Look up the element rto add
    producer_element = Element.objects.get(pk=form_values['producer_element_id'])

    # TODO: various use cases
        # - component previously added but element has statements not yet added to system
        #   this issue may be best addressed elsewhere.

    # Component already added to system. Do not add the component (element) to the system again.
    if producer_element.id in elements_selected_ids:
        messages.add_message(request, messages.ERROR,
                            f'Component "{producer_element.name}" already exists in selected components.')
        # Redirect to selected element page
        return HttpResponseRedirect("/systems/{}/components/selected".format(system_id))

    smts = Statement.objects.filter(producer_element_id = producer_element.id, statement_type="control_implementation_prototype")

    # Component does not have any statements of type control_implementation_prototype to
    # add to system. So we cannot add the component (element) to the system.
    if len(smts) == 0:
        # print(f"The component {producer_element.name} does not have any control implementation statements.")
        messages.add_message(request, messages.ERROR,
                            f'I couldn\'t add "{producer_element.name}" to the system because the component does not currently have any control implementation statements to add.')
        # Redirect to selected element page
        return HttpResponseRedirect("/systems/{}/components/selected".format(system_id))

    # Loop through element's prototype statements and add to control implementation statements
    for smt in Statement.objects.filter(producer_element_id = producer_element.id, statement_type="control_implementation_prototype"):
        # Add all existsing control statements for a component to a system even if system does not use controls.
        # This guarantees that control statements are associated.
        # The selected controls will serve as the primary filter on what content to display.
        smt.create_instance_from_prototype(system.root_element.id)

    # Make sure some controls were added to the system. Report error otherwise.
    smts_added = Statement.objects.filter(producer_element_id = producer_element.id, consumer_element_id = system.root_element.id, statement_type="control_implementation")
    print("DEBUG smts_added ", smts_added)
    smts_added_count = len(smts_added)
    if smts_added_count > 0:
        messages.add_message(request, messages.INFO,
                         f'OK. I\'ve added "{producer_element.name}" to the system and its {smts_added_count} control implementation statements to the system.')
    else:
        messages.add_message(request, messages.WARNING,
                         f'Oops. I tried adding "{producer_element.name}" to the system, but the component added 0 controls.')

    # Redirect to selected element page
    return HttpResponseRedirect("/systems/{}/components/selected".format(system_id))

def search_system_component(request):
    """Add an existing element and its statements to a system"""

    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    form_dict = dict(request.GET)
    form_values = {}
    for key in form_dict.keys():
        form_values[key] = form_dict[key][0]
    # Form values from ajax data

    if "system_id" in form_values.keys():
        system_id = form_values['system_id']

        # Does user have permission to add element?
        # Check user permissions
        system = System.objects.get(pk=system_id)

        if not request.user.has_perm('change_system', system):
            # User does not have write permissions
            # Log permission to save answer denied
            logger.info(
                event="change_system permission_denied",
                object={"object": "element", "producer_element_name": form_values['producer_element_name']},
                user={"id": request.user.id, "username": request.user.username}
            )
            return HttpResponseForbidden("Permission denied. {} does not have change privileges to system and/or project.".format(request.user.username))

        selected_controls = system.root_element.controls.all()
        selected_controls_ids = set()
        for sc in selected_controls:
            selected_controls_ids.add("{} {}".format(sc.oscal_ctl_id, sc.oscal_catalog_key))

        # Add element
        # Look up the element

        text =  form_values['text']

        # The final elements that are returned to the new dropdown created...
        producer_system_elements = Element.objects.filter(element_type="system_element").filter(name__contains= text)

        producer_elements = [{"id":str(ele.id), "name": ele.name} for ele in producer_system_elements]

        results = {'producer_element_statement_values': producer_elements}
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    # # Redirect to selected element page
    # return HttpResponseRedirect("/systems/{}/components/selected".format(system_id))

class RelatedComponentStatements(View):
    """
    Returns the component statements that are produced(related) to one control implementation prototype
    """

    template_name = 'controls/editor.html'

    def get(self, request):
        """Add an existing element and its statements to a system"""

        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        logger.info(f"Related controls GET: {dict(request.GET)}")
        form_dict = dict(request.GET)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]
        # Form values from ajax data

        if "system_id" in form_values.keys():
            system_id = form_values['system_id']

            # Does user have permission to add element?
            # Check user permissions
            system = System.objects.get(pk=system_id)

            if not request.user.has_perm('change_system', system):
                # User does not have write permissions
                # Log permission to save answer denied
                logger.info(
                    event="change_system permission_denied",
                    object={"object": "element", "producer_element_name": form_values['producer_element_name']},
                    user={"id": request.user.id, "username": request.user.username}
                )
                return HttpResponseForbidden(
                    "Permission denied. {} does not have change privileges to system and/or project.".format(
                        request.user.username))

            selected_controls = system.root_element.controls.all()
            selected_controls_ids = set()
            for sc in selected_controls:
                selected_controls_ids.add("{} {}".format(sc.oscal_ctl_id, sc.oscal_catalog_key))

            # Add element
            # Look up the element
            producer_element_id = form_values['producer_element_form_id']
            producer_element = Element.objects.get(pk=producer_element_id)

            # The final elements that are returned to the new dropdown created...
            producer_smt_imps = producer_element.statements("control_implementation")

            producer_smt_imps_vals = [{"smt_id": str(smt.id), "smt_sid": smt.sid, "smt_sid_class": smt.sid_class,  "producer_element_name": producer_element.name, "smt_body":str(smt.body), "smt_pid":str(smt.pid), "smt_status":str(smt.status)} for smt in producer_smt_imps]

            results = {'producer_element_statement_values': producer_smt_imps_vals,  "selected_component": producer_element.name}
            data = json.dumps(results)
            mimetype = 'application/json'
            if data:
                return HttpResponse(data, mimetype)
            else:
                return JsonResponse(status=400, data={'status': 'error', 'message': f"No DATA!: {data}"})
        else:
            return JsonResponse(status=400, data={'status': 'error', 'message': "There is no current system id present"})

class EditorAutocomplete(View):
    template_name = 'controls/editor.html'

    def get(self, request):
        """Add an existing element and its statements to a system"""

        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        form_dict = dict(request.GET)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]
        # Form values from ajax data

        if "system_id" in form_values.keys():
            system_id = form_values['system_id']

            # Does user have permission to add element?
            # Check user permissions
            system = System.objects.get(pk=system_id)

            if not request.user.has_perm('change_system', system):
                # User does not have write permissions
                # Log permission to save answer denied
                logger.info(
                    event="change_system permission_denied",
                    object={"object": "element", "producer_element_name": form_values['producer_element_name']},
                    user={"id": request.user.id, "username": request.user.username}
                )
                return HttpResponseForbidden(
                    "Permission denied. {} does not have change privileges to system and/or project.".format(
                        request.user.username))

            selected_controls = system.root_element.controls.all()
            selected_controls_ids = set()
            for sc in selected_controls:
                selected_controls_ids.add("{} {}".format(sc.oscal_ctl_id, sc.oscal_catalog_key))

            # Add element
            # Look up the element

            text = form_values['text']

            # The final elements that are returned to the new dropdown created...
            producer_system_elements = Element.objects.filter(element_type="system_element").filter(name__contains=text)

            producer_elements = [{"id": str(ele.id), "name": ele.name} for ele in producer_system_elements]

            results = {'producer_element_name_value': producer_elements}
            data = json.dumps(results)
            mimetype = 'application/json'
            if data:
                return HttpResponse(data, mimetype)
            else:
                return JsonResponse(status=400, data={'status': 'error', 'message': f"No statements found with the search: {text}"})
        else:
            return JsonResponse(status=400, data={'status': 'error', 'message': "There is no current system id present"})

    def post(self, request, system_id):
        """Add an existing element and its statements to a system"""
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        form_dict = dict(request.POST)

        form_values = {}
        for key in form_dict.keys():
            if key == 'relatedcomps':
                form_values[key] = form_dict[key]
            else:
                form_values[key] = form_dict[key][0]
        # Form values from ajax data

        if "system_id" in form_values.keys():
            system_id = form_values['system_id']
            # Does user have permission to add element?
            # Check user permissions
            system = System.objects.get(pk=system_id)
            if not request.user.has_perm('change_system', system):
                # User does not have write permissions
                # Log permission to save answer denied
                logger.info(
                    event="change_system permission_denied",
                    object={"object": "element", "entered_producer_element_name": form_values['text'] or "None"},
                    user={"id": request.user.id, "username": request.user.username}
                )
                return HttpResponseForbidden(
                    "Permission denied. {} does not have change privileges to system and/or project.".format(
                        request.user.username))

            selected_controls = system.root_element.controls.all()
            selected_controls_ids = set()
            for sc in selected_controls:
                selected_controls_ids.add("{} {}".format(sc.oscal_ctl_id, sc.oscal_catalog_key))

            # Add element
            if form_values.get("relatedcomps", ""):

                for related_element in form_values['relatedcomps']:

                    # Look up the element
                    for smt in Statement.objects.filter(id=related_element, statement_type="control_implementation"):
                        logger.info(
                            f"Adding an element with the id {smt.id} and sid class {smt.sid} to system_id {system_id}")
                        # Only add statements for controls selected for system
                        if "{} {}".format(smt.sid, smt.sid_class) in selected_controls_ids:
                            logger.info(f"smt {smt}")
                            smt.create_instance_from_prototype(system.root_element.id)
                        else:
                            logger.error(f"not adding smt from selected controls for the current system: {smt}")

        # Redirect to the page where the component was added from
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# Baselines

def assign_baseline(request, system_id, catalog_key, baseline_name):
    """Assign a baseline to a system root element thereby showing selected controls for the system."""

    system = System.objects.get(pk=system_id)
    #system.root_element.assign_baseline_controls(user, 'NIST_SP-800-53_rev4', 'low')
    assign_results = system.root_element.assign_baseline_controls(request.user, catalog_key, baseline_name)
    if assign_results:
        messages.add_message(request, messages.INFO,
                             'Baseline "{} {}" assigned.'.format(catalog_key.replace("_", " "), baseline_name.title()))
        # Log start app / new project
        logger.info(
            event="assign_baseline",
            object={"object": "system", "id": system.root_element.id, "title": system.root_element.name},
            baseline={"catalog_key": catalog_key, "baseline_name": baseline_name},
            user={"id": request.user.id, "username": request.user.username}
        )
    else:
        messages.add_message(request, messages.ERROR,
                             'Baseline "{} {}" assignment failed.'.format(catalog_key.replace("_", " "),
                                                                          baseline_name.title()))

    return HttpResponseRedirect(f"/systems/{system_id}/controls/selected")


# Export OpenControl

def export_system_opencontrol(request, system_id):
    """Export entire system in OpenControl"""

    # Does user have permission
    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]

        # Create temporary directory structure
        import tempfile
        temp_dir = tempfile.TemporaryDirectory(dir=".")
        repo_path = os.path.join(temp_dir.name, system.root_element.name.replace(" ", "_"))
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        # Create various directories
        os.makedirs(os.path.join(repo_path, "components"))
        os.makedirs(os.path.join(repo_path, "standards"))
        os.makedirs(os.path.join(repo_path, "certifications"))

        # Create opencontrol.yaml config file
        cfg_str = """schema_version: 1.0.0
name: ~
metadata:
  authorization_id: ~
  description: ~
  organization:
    name: ~
    abbreviation: ~
  repository: ~
components: []
standards:
- ./standards/NIST-SP-800-53-rev4.yaml
certifications:
- ./certifications/fisma-low-impact.yaml
"""

        # read default opencontrol.yaml into object
        cfg = rtyaml.load(cfg_str)
        # customize values
        cfg["name"] = system.root_element.name
        # cfg["metadata"]["organization"]["name"] = organization_name
        # cfg["metadata"]["description"] = description
        # cfg["metadata"]["organization"]["abbreviation"] = None
        # if organization_name:
        #     cfg["metadata"]["organization"]["abbreviation"] = "".join([word[0].upper() for word in organization_name.split(" ")])

        with open(os.path.join(repo_path, "opencontrol.yaml"), 'w') as outfile:
            outfile.write(rtyaml.dump(cfg))

        # Populate reference directories from reference
        OPENCONTROL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'opencontrol')
        shutil.copyfile(os.path.join(OPENCONTROL_PATH, "standards", "NIST-SP-800-53-rev4.yaml"),
                        os.path.join(repo_path, "standards", "NIST-SP-800-53-rev4.yaml"))
        shutil.copyfile(os.path.join(OPENCONTROL_PATH, "standards", "NIST-SP-800-171r1.yaml"),
                        os.path.join(repo_path, "standards", "NIST-SP-800-53-rev4.yaml"))
        shutil.copyfile(os.path.join(OPENCONTROL_PATH, "standards", "opencontrol.yaml"),
                        os.path.join(repo_path, "standards", "opencontrol.yaml"))
        shutil.copyfile(os.path.join(OPENCONTROL_PATH, "standards", "hipaa-draft.yaml"),
                        os.path.join(repo_path, "standards", "hipaa-draft.yaml"))
        shutil.copyfile(os.path.join(OPENCONTROL_PATH, "certifications", "fisma-low-impact.yaml"),
                        os.path.join(repo_path, "certifications", "fisma-low-impact.yaml"))

        # # Make stub README.md file
        # with open(os.path.join(repo_path, "README.md"), 'w') as outfile:
        #     outfile.write("Machine readable representation of 800-53 control implementations for {}.\n\n# Notes\n\n".format(system_name))
        #     print("wrote file: {}\n".format(os.path.join(repo_path, "README.md")))

        # Populate system information files

        # Populate component files
        if not os.path.exists(os.path.join(repo_path, "components")):
            os.makedirs(os.path.join(repo_path, "components"))
        for element in system.producer_elements:
            # Build OpenControl
            ocf = {
                "name": element.name,
                "schema_version": "3.0.0",
                "documentation_complete": False,
                "satisfies": []
            }
            satisfies_smts = ocf["satisfies"]
            # Retrieve impl_smts produced by element and consumed by system
            # Get the impl_smts contributed by this component to system
            impl_smts = element.statements_produced.filter(consumer_element=system.root_element)
            for smt in impl_smts:
                my_dict = {
                    "control_key": smt.sid.upper(),
                    "control_name": smt.catalog_control_as_dict['title'],
                    "standard_key": smt.sid_class,
                    "covered_by": [],
                    "security_control_type": "Hybrid | Inherited | ...",
                    "narrative": [
                        {"text": smt.body}
                    ],
                    "remarks": [
                        {"text": smt.remarks}
                    ]
                }
                satisfies_smts.append(my_dict)
            opencontrol_string = rtyaml.dump(ocf)
            # Write component file
            with open(os.path.join(repo_path, "components", "{}.yaml".format(element.name.replace(" ", "_"))), 'w') as fh:
                fh.write(opencontrol_string)

        # Build Zip archive
        # TODO Make Temporary File
        #      Current approach leads to race conditions!
        shutil.make_archive("/tmp/Zipped_file", 'zip', repo_path)

        # Download Zip archive of OpenControl files
        with open('/tmp/Zipped_file.zip', 'rb') as tmp:
            tmp.seek(0)
            stream = tmp.read()
            blob = stream
        mime_type = "application/octet-stream"
        filename = "{}-opencontrol-{}.zip".format(system.root_element.name.replace(" ", "_"),
                                                  datetime.now().strftime("%Y-%m-%d-%H-%M"))

        resp = HttpResponse(blob, mime_type)
        resp['Content-Disposition'] = 'inline; filename=' + filename

        # Clean up
        shutil.rmtree(repo_path)
        # os.remove("/tmp/Zipped_file") ????
        return resp

    else:
        # User does not have permission to this system
        raise Http404


# PoamS
def poams_list(request, system_id):
    """List PoamS for a system"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        controls = system.root_element.controls.all()
        poam_smts = system.root_element.statements_consumed.filter(statement_type="POAM").order_by('-updated')

        # impl_smts_count = {}
        # ikeys = system.smts_control_implementation_as_dict.keys()
        # for c in controls:
        #     impl_smts_count[c.oscal_ctl_id] = 0
        #     if c.oscal_ctl_id in ikeys:
        #         impl_smts_count[c.oscal_ctl_id] = len(system.smts_control_implementation_as_dict[c.oscal_ctl_id]['control_impl_smts'])

        # Return the controls
        context = {
            "system": system,
            "project": project,
            "controls": controls,
            "poam_smts": poam_smts,
            "enable_experimental_opencontrol": SystemSettings.enable_experimental_opencontrol,
            "enable_experimental_oscal": SystemSettings.enable_experimental_oscal,
            "project_form": ProjectForm(request.user),
        }
        return render(request, "systems/poams_list.html", context)
    else:
        # User does not have permission to this system
        raise Http404


def new_poam(request, system_id):
    """Form to create new POAM"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        controls = system.root_element.controls.all()

        if request.method == 'POST':
            statement_form = StatementPoamForm(request.POST)
            # if statement_form.is_valid() and poam_form.is_valid():
            if statement_form.is_valid():
                statement = statement_form.save()
                poam_form = PoamForm(request.POST)
                if poam_form.is_valid():
                    poam = poam_form.save()
                    print('POAM ID', poam.get_next_poam_id(system))
                    poam.poam_id = poam.get_next_poam_id(system)
                    poam.statement = statement
                    poam.save()
                return HttpResponseRedirect('/systems/{}/poams'.format(system_id), {})
                #url(r'^(?P<system_id>.*)/poams$', views.poams_list, name="poams_list"),
            else:
                pass
        else:
            statement_form = StatementPoamForm(status="Open", statement_type="POAM", consumer_element=system.root_element)
            poam = Poam()
            poam_id = poam.get_next_poam_id(system)
            poam_form = PoamForm()
            return render(request, 'systems/poam_form.html', {
                'statement_form': statement_form,
                'poam_form': poam_form,
                'system': system,
                'project': project,
                'controls': controls,
                "project_form": ProjectForm(request.user),
            })
    else:
        # User does not have permission to this system
        raise Http404


def edit_poam(request, system_id, poam_id):
    """Form to create new POAM"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve primary system Project
        # Temporarily assume only one project and get first project
        project = system.projects.all()[0]
        controls = system.root_element.controls.all()
        # Retrieve POAM Statement
        poam_smt = get_object_or_404(Statement, id=poam_id)

        if request.method == 'POST':
            statement_form = StatementPoamForm(request.POST, instance=poam_smt)
            poam_form = PoamForm(request.POST, instance=poam_smt.poam)
            if statement_form.is_valid() and poam_form.is_valid():
                # Save statement after updating values
                statement_form.save()
                poam_form.save()
                return HttpResponseRedirect('/systems/{}/poams'.format(system_id), {})
            else:
                pass
                #TODO: What if form invalid?
        else:
            statement_form = StatementPoamForm(initial={
                'statement_type': poam_smt.statement_type,
                'status': poam_smt.status,
                'consumer_element': system.root_element,
                'body': poam_smt.body,
                'remarks': poam_smt.remarks,
            })
            poam_form = PoamForm(initial={
                'weakness_name': poam_smt.poam.weakness_name,
                'controls': poam_smt.poam.controls,
                'poam_group': poam_smt.poam.poam_group,
                'risk_rating_original': poam_smt.poam.risk_rating_original,
                'risk_rating_adjusted': poam_smt.poam.risk_rating_adjusted,
                'weakness_detection_source': poam_smt.poam.weakness_detection_source,
                'remediation_plan': poam_smt.poam.remediation_plan,
                'milestones': poam_smt.poam.milestones,
                'scheduled_completion_date': poam_smt.poam.scheduled_completion_date,
            })
            return render(request, 'systems/poam_edit_form.html', {
                'statement_form': statement_form,
                'poam_form': poam_form,
                'system': system,
                'project': project,
                'controls': controls,
                'poam_smt': poam_smt,
                "project_form": ProjectForm(request.user),
            })
    else:
        # User does not have permission to this system
        raise Http404


def poam_export_xlsx(request, system_id):
    return poam_export(request, system_id, 'xlsx')


def poam_export_csv(request, system_id):
    return poam_export(request, system_id, 'csv')


def poam_export(request, system_id, format='xlsx'):
    """Export POA&M in either xlsx or csv"""

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related selected POA&Ms if user has permission on system
    if request.user.has_perm('view_system', system):

        if format == 'xlsx':
            from openpyxl import Workbook
            from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment
            from tempfile import NamedTemporaryFile

            wb = Workbook()
            ws = wb.active
            # create alignment style
            wrap_alignment = Alignment(wrap_text=True)
            ws.title = "POA&Ms"
        else:
            import csv, io
            csv_buffer = io.StringIO(newline='\n')
            csv_writer = csv.writer(csv_buffer)

        poam_fields = [
            {'var_name': 'poam_id', 'name': 'POA&M ID', 'width': 8},
            {'var_name': 'poam_group', 'name': 'POA&M Group', 'width': 16},
            {'var_name': 'weakness_name', 'name': 'Weakness Name', 'width': 24},
            {'var_name': 'controls', 'name': 'Controls', 'width': 16},
            {'var_name': 'body', 'name': 'Description', 'width': 60},
            {'var_name': 'status', 'name': 'Status', 'width': 8},
            {'var_name': 'risk_rating_original', 'name': 'Risk Rating Original', 'width': 16},
            {'var_name': 'risk_rating_adjusted', 'name': 'Risk Rating Adjusted', 'width': 16},
            {'var_name': 'weakness_detection_source', 'name': 'Weakness Detection Source', 'width': 24},
            {'var_name': 'weakness_source_identifier', 'name': 'Weakness Source Identifier', 'width': 24},
            {'var_name': 'remediation_plan', 'name': 'Remediation Plan', 'width': 60},
            {'var_name': 'milestones', 'name': 'Milestones', 'width': 60},
            {'var_name': 'milestone_changes', 'name': 'Milestone Changes', 'width': 30},
            {'var_name': 'scheduled_completion_date', 'name': 'Scheduled Completion Date', 'width': 18},
        ]

        # create header row
        column = 0
        ord_zeroth_column = ord('A') - 1
        csv_row = []

        for poam_field in poam_fields:
            column += 1
            if format == 'xlsx':
                c = ws.cell(row=1, column=column, value=poam_field['name'])
                c.fill = PatternFill("solid", fgColor="5599FE")
                c.font = Font(color="FFFFFF", bold=True)
                c.border = Border(left=Side(border_style="thin", color="444444"),
                                  right=Side(border_style="thin", color="444444"),
                                  bottom=Side(border_style="thin", color="444444"),
                                  outline=Side(border_style="thin", color="444444"))
                ws.column_dimensions[chr(ord_zeroth_column + column)].width = poam_field['width']
            else:
                csv_row.append(poam_field['name'])
        # Add column for URL
        if format == 'xlsx':
            c = ws.cell(row=1, column=column, value="URL")
            c.fill = PatternFill("solid", fgColor="5599FE")
            c.font = Font(color="FFFFFF", bold=True)
            c.border = Border(left=Side(border_style="thin", color="444444"),
                              right=Side(border_style="thin", color="444444"),
                              bottom=Side(border_style="thin", color="444444"),
                              outline=Side(border_style="thin", color="444444"))
            ws.column_dimensions[chr(ord_zeroth_column + column)].width = 60
        else:
            csv_row.append('URL')

        if format != 'xlsx':
            csv_writer.writerow(csv_row)

        # Retrieve POA&Ms and create POA&M rows
        poam_smts = system.root_element.statements_consumed.filter(statement_type="POAM").order_by('id')
        poam_smts_by_sid = {}
        row = 1
        for poam_smt in poam_smts:
            csv_row = []
            row += 1

            # Loop through fields
            column = 0
            for poam_field in poam_fields:
                column += 1
                if format == 'xlsx':
                    if poam_field['var_name'] in ['body', 'status']:
                        c = ws.cell(row=row, column=column, value=getattr(poam_smt, poam_field['var_name']))
                    else:
                        if poam_field['var_name'] == 'poam_id':
                            c = ws.cell(row=row, column=column,
                                        value="V-{}".format(getattr(poam_smt.poam, poam_field['var_name'])))
                        else:
                            c = ws.cell(row=row, column=column, value=getattr(poam_smt.poam, poam_field['var_name']))
                    c.fill = PatternFill("solid", fgColor="FFFFFF")
                    c.alignment = Alignment(vertical='top', horizontal='left', wrapText=True)
                    c.border = Border(right=Side(border_style="thin", color="444444"),
                                      bottom=Side(border_style="thin", color="444444"),
                                      outline=Side(border_style="thin", color="444444"))
                else:
                    if poam_field['var_name'] in ['body', 'status']:
                        csv_row.append(getattr(poam_smt, poam_field['var_name']))
                    else:
                        if poam_field['var_name'] == 'poam_id':
                            csv_row.append("V-{}".format(getattr(poam_smt.poam, poam_field['var_name'])))
                        else:
                            csv_row.append(getattr(poam_smt.poam, poam_field['var_name']))

            # Add URL column
            poam_url = settings.SITE_ROOT_URL + "/systems/{}/poams/{}/edit".format(system_id, poam_smt.id)
            if format == 'xlsx':
                c = ws.cell(row=row, column=column, value=poam_url)
                c.fill = PatternFill("solid", fgColor="FFFFFF")
                c.alignment = Alignment(vertical='top', horizontal='left', wrapText=True)
                c.border = Border(right=Side(border_style="thin", color="444444"),
                                  bottom=Side(border_style="thin", color="444444"),
                                  outline=Side(border_style="thin", color="444444"))
            else:
                csv_row.append(poam_url)

            if format != 'xlsx':
                csv_writer.writerow(csv_row)

        if format == 'xlsx':
            with NamedTemporaryFile() as tmp:
                wb.save(tmp.name)
                tmp.seek(0)
                stream = tmp.read()
                blob = stream
        else:
            blob = csv_buffer.getvalue()
            csv_buffer.close()

        # Determine filename based on system name
        system_name = system.root_element.name.replace(" ", "_") + "_" + system_id
        filename = "{}_poam_export-{}.{}".format(system_name, datetime.now().strftime("%Y-%m-%d-%H-%M"), format)
        mime_type = "application/octet-stream"

        resp = HttpResponse(blob, mime_type)
        resp['Content-Disposition'] = 'inline; filename=' + filename
        return resp
    else:
        # User does not have permission to this system
        raise Http404

def project_import(request, project_id):
    """
    Import an entire project's components and control content
    """
    project = Project.objects.get(id=project_id)
    # Retrieve identified System
    if request.method == 'POST':
        project_data = request.POST['json_content']
        importcheck = False
        if "importcheck" in request.POST:
            importcheck = request.POST["importcheck"]

        # We are just updating the current project
        if importcheck == False:
            logger.info(
                event="project JSON import update",
                object={"object": "project", "id": project.id, "title": project.title},
                user={"id": request.user.id, "username": request.user.username}
            )
            messages.add_message(request, messages.INFO, 'The current project was updated.')
        else:
            # Creating a new project
            new_project = Project.objects.create(organization=project.organization)
            # Need to get or create the app source by the id of the given app source
            src = AppSource.objects.get(id=request.POST["appsource_compapp"])
            app = AppVersion.objects.get(source=src, id=request.POST["appsource_version_id"])
            module_name = json.loads(project_data).get('project').get('module').get('key')
            root_task = Task.objects.create(
                module=Module.objects.get(app=app, module_name=module_name),
                project=project, editor=request.user)# TODO: Make sure the root task created here is saved
            new_project.root_task = root_task
            # Need new element to for the new System
            element = Element()
            project_names = Element.objects.filter(element_type="system").values_list('name', flat=True)
            # If it is a new title just make that the new system name otherwise increment
            new_title = new_project.title
            if new_title not in project_names:
                new_title = new_project.title
            else:
                while new_title in project_names:
                    new_title = increment_element_name(new_title)

            element.name = new_title
            element.element_type = "system"
            element.save()
            # Create system
            system = System(root_element=element)
            system.save()
            new_project.system = system
            new_project.portfolio = project.portfolio
            project = new_project
            project.save()
            messages.add_message(request, messages.INFO, f'Created a new project with id: {project.id}.')

        #Import questionnaire data
        log_output = []
        try:
            from collections import OrderedDict
            data = json.loads(project_data, object_pairs_hook=OrderedDict)
        except Exception as e:
            log_output.append("There was an error reading the export file.")
        else:
            try:
                # Update project data.
                project.import_json(data, request.user, "imp", lambda x: log_output.append(x))
            except Exception as e:
                log_output.append(str(e))

        # Log output
        logger.info(
            event="project JSON import",
            object={"object": "project", "id": project.id, "title": project.title, "log_output": log_output},
            user={"id": request.user.id, "username": request.user.username}
        )
        loaded_imported_jsondata = json.loads(project_data)
        if loaded_imported_jsondata.get('component-definitions') != None:
            # Load and get the components then dump
            for k, val in enumerate(loaded_imported_jsondata.get('component-definitions')):
                oscal_component_json = json.dumps(loaded_imported_jsondata.get('component-definitions')[k])
                import_name = request.POST.get('import_name', '')
                result = ComponentImporter().import_components_as_json(import_name, oscal_component_json, request)

        return HttpResponseRedirect("/projects")

def project_export(request, project_id):
    """
    Export an entire project's components and control content
    """
    # Of the project in the current system. pick one project to export
    project = Project.objects.get(id=project_id)
    system_id = project.system.id
    # Retrieve identified System
    system = System.objects.get(id=system_id)

    # Retrieve related selected controls if user has permission on system
    if request.user.has_perm('view_system', system):

        # Iterate through the elements associated with the system get all statements produced for each
        oscal_comps = []
        for element in system.producer_elements:
            # Implementation statement OSCAL JSON
            impl_smts = element.statements_produced.filter(consumer_element=system.root_element)
            component = OSCALComponentSerializer(element, impl_smts).as_json()
            oscal_comps.append(component)

    # TODO: multiple export types

    questionnaire_data = json.dumps(project.export_json(include_metadata=True, include_file_content=True))
    data = json.loads(questionnaire_data)
    data['component-definitions'] = [json.loads(oscal_comp) for oscal_comp in oscal_comps]
    response = JsonResponse(data, json_dumps_params={"indent": 2})
    filename = project.title.replace(" ", "_") + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M")
    response['Content-Disposition'] = f'attachment; filename="{quote(filename)}.json"'
    return response
