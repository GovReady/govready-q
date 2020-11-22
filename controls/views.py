from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, \
    HttpResponseNotAllowed
from django.forms import ModelForm
from django.views import View
from siteapp.models import Project, User, Organization
from siteapp.forms import PortfolioForm, ProjectForm
from datetime import datetime
from .oscal import Catalog, Catalogs
import json, rtyaml, shutil, re, os
from .utilities import *
from .models import *
from system_settings.models import SystemSettings
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)

import logging
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

    # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattened_controls_all_as_dict()

    # Handle properly formatted control id that does not exist
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", {"control": {}})

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
        impl_smts = element.statements_produced.filter(consumer_element=system.root_element,
                                                       statement_type="control_implementation")

        # Retrieve used catalog_key
        catalog_key = impl_smts[0].sid_class

        # Retrieve control ids
        catalog_controls = Catalog.GetInstance(catalog_key=catalog_key).get_controls_all()

        # Build OSCAL
        # Example: https://github.com/usnistgov/OSCAL/blob/master/src/content/ssp-example/json/example-component.json
        of = {
            "metadata": {
                "title": "{} Component-to-Control Narratives".format(element.name),
                "published": datetime.now().replace(microsecond=0).isoformat(),
                "last-modified": element.updated.replace(microsecond=0).isoformat(),
                "version": "string",
                "oscal-version": "1.0.0-milestone2",
            },
            "component": {
                "name": element.name,
                "component-type": element.element_type,
                "title": element.full_name,
                "description": element.description,
                "properties": [],
                "links": [],
                "control-implementation": {
                    "description": "",
                    "can-meet-requirement-sets": [
                        {
                            "source": "url-reference",
                            "description": "text",
                            "properties": [],
                            "links": [],
                            "implemented-requirement": {
                                "requirement-id": "",
                                "id": "",
                                "control-id": "",
                            },
                            "remarks": ""
                        }
                    ]
                },
                "remarks": "text, parsed as Markdown (multiple lines) [0 or 1]"
            },
            "back-matter": []
        }
        implemented_requirement = of["component"]["control-implementation"]["can-meet-requirement-sets"][0][
            "implemented-requirement"]
        for smt in impl_smts:
            my_dict = {
                smt.sid + "_smt": {
                    "description": smt.body,
                    "properties": [],
                    "links": [],
                    "remarks": smt.remarks
                },
            }
            implemented_requirement.update(my_dict)
        oscal_string = json.dumps(of, sort_keys=False, indent=2)

        # Build OpenControl
        ocf = {
            "name": element.name,
            "schema_version": "3.0.0",
            "documentation_complete": False,
            "satisfies": []
        }

        satisfies_smts = ocf["satisfies"]
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
            # print(control)
            if control.oscal_ctl_id in impl_smts_by_sid:
                setattr(control, 'impl_smts', impl_smts_by_sid[control.oscal_ctl_id])
                # print(control.oscal_ctl_id, control.impl_smts)
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

    # Get control catalog
    catalog = Catalog(catalog_key)

    # TODO: maybe catalogs could provide an API that returns a set of 
    # control ids instead?

    cg_flat = catalog.get_flattened_controls_all_as_dict()

    # If control id does not exist in catalog
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", {"control": {}})

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
                                    "component-logging-policy": {
                                        "description": "The legal department develops, documents, and disseminates this policy to all staff and contractors within the organization.",
                                        "role-ids": "legal-officer",
                                        "set-params": {
                                            "{}_prm_1".format(cl_id): {
                                                "value": ""
                                            }
                                        }
                                    }
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
            # print(smt.id, smt.body)
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
        elements = Element.objects.exclude(element_type='system').filter(
            element_type="system_element",
            statements_produced__sid=cl_id,
            statements_produced__statement_type="control_implementation_prototype",
        )
        print("elements queryset")
        print(elements)
        print(len(elements))

       # elements =  Element.objects.all().exclude(element_type='system')

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


class EditorAutocomplete(View):
    template_name = 'controls/editor.html'

    def get(self, request):
        """Add an existing element and its statements to a system"""
        print("searchhhh_system_component request")
        print(request)
        print(request.method)
        print("system_id")
        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        print(dict(request.GET))
        form_dict = dict(request.GET)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]
        # Form values from ajax data

        if "system_id" in form_values.keys():
            system_id = form_values['system_id']
            # TODO: get producer element id from system id and/or statement

            producer_element_id = form_values['producer_element_form_id']
            # Does user have permission to add element?
            # Check user permissions
            system = System.objects.get(pk=system_id)
            print("system")
            print(system)
            #system = System.objects.get(pk=system_id)
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
            print("selected_controls_ids")
            print(selected_controls_ids)
            print("selected_controls")
            print(selected_controls)
            # Add element
            # Look up the element
            producer_element = Element.objects.get(pk=producer_element_id)
            print("producer_element")
            print(producer_element)
            # TODO: Handle case of element already associated with system

            cl_id = form_values['control_id']  #"ac-2"#oscalize_control_id(cl_id)
            text = form_values['text']
            print("cl_id")
            print(cl_id)
            print("text")
            print(text)
            # The final elements that are returned to the new dropdown created...
            #producer_system_elements = Element.objects.filter(element_type="system_element").filter(name__contains=text)
            producer_system_elements = Element.objects.exclude(element_type='system').filter(
                element_type="system_element",
                statements_produced__sid=cl_id,
                statements_produced__statement_type="control_implementation_prototype",
            ).filter(name__contains=text)
            print("producer_system_elements")
            print(producer_system_elements)

            # only prototype implementation statements for the given control
            #control_ids = Statement.objects.filter(statement_type="control_implementation_prototype").filter(sid=cl_id)
            # print("control_ids")
            # print(control_ids)
            #  for contorl_id in control_ids:
            #      filtered_by_element_name = Element.objects.filter(id=contorl_id.producer_element_id)
            #      # Element.objects.get(pk=producer_element_id)
            #      # filtered_by_element_name = Element.filter(name__contains= text)
            #      print("filtered_by_element_name")
            #      print(filtered_by_element_name)
            # Loop through element's prototype statements and add to control implementation statements
            #print("Adding {} to system_id {}".format(producer_element.name, system_id))
            # for smt in Statement.objects.filter(producer_element_id = producer_element.id, statement_type="control_implementation_prototype"):
            #     # Only add statements for controls selected for system
            #     if "{} {}".format(smt.sid, smt.sid_class) in selected_controls_ids:
            #         print("smt", smt)
            #         smt.create_instance_from_prototype(system.root_element.id)
            #     else:
            #         print("not adding smt not selected controls for system", smt)

            producer_elements = [{"id": str(ele.id), "name": ele.name} for ele in producer_system_elements]
            print("producer_elements")
            print(producer_elements)
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
        print("addinggggg_system_component request")
        print(request)
        print(request.method)
        print("system_id")
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        print(dict(request.POST))
        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]
        # Form values from ajax data

        if "system_id" in form_values.keys():
            # This returns all the elements by system element and control id
            # for system_ele in producer_system_elements:
            #     filtered_by_element_name2 = Statement.objects.filter(sid=cl_id).filter(producer_element_id=system_ele)
            #     # Element.objects.get(pk=producer_element_id)
            #     # filtered_by_element_name = Element.filter(name__contains= text)
            #     print("filtered_by_element_name2")
            #     print(filtered_by_element_name2)

            system_id = form_values['system_id']
            producer_element_id = form_values['selected_producer_element_form_id']
            # Does user have permission to add element?
            # Check user permissions
            system = System.objects.get(pk=system_id)
            print("system")
            print(system)
            #system = System.objects.get(pk=system_id)
            if not request.user.has_perm('change_system', system):
                # User does not have write permissions
                # Log permission to save answer denied
                logger.info(
                    event="change_system permission_denied",
                    object={"object": "element", "entered_producer_element_name": form_values['text']},
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
            producer_element = Element.objects.get(pk=producer_element_id)
            # TODO: Handle case of element already associated with system

            # Loop through element's prototype statements and add to control implementation statements
            print("Adding {} to system_id {}".format(producer_element.name, system_id))
            for smt in Statement.objects.filter(producer_element_id=producer_element.id,
                                                statement_type="control_implementation_prototype"):
                # Only add statements for controls selected for system
                if "{} {}".format(smt.sid, smt.sid_class) in selected_controls_ids:
                    print("smt", smt)
                    smt.create_instance_from_prototype(system.root_element.id)
                else:
                    print("not adding smt not selected controls for system", smt)


        # Redirect to the page where the component was added from
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def editor_compare(request, system_id, catalog_key, cl_id):
    """System Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get control catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattened_controls_all_as_dict()
    # If control id does not exist in catalog
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", {"control": {}})

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


def get_control_elements(request):
    #what was in the question an array is now a python list of dicts.
    #it can also be in some other file and just imported.
    # all_city_names = [
    # { "good_name": 'Palma', "input_name": 'Palma de Mallorca' },
    # { "good_name": 'Mallorca', "input_name": 'Mallorca' },
    # { "good_name": 'Majorca', "input_name": 'Majorca' },
    # # etc
    # ]

    if request.method == 'POST':
        q = request.POST.get('autocomplete_name', '')

        cl_id = "ac-2"#oscalize_control_id(cl_id)
        # only prototype implementation statements for the given control
        proto_impl_smts = Statement.objects.filter(statement_type="control_implementation_prototype").filter(sid=cl_id)
        print("proto_impl_smts")
        print(proto_impl_smts)
        proto_data = serializers.serialize('json', proto_impl_smts)
        proto_data = json.loads(proto_data)
        print("proto_data")
        print(proto_data)
        for p_data in proto_data:
            print(p_data.get('fields').get('sid'))
        # STEP 1
        # Getting elements that contain the name provided in the text search
        search_qs = Element.objects.filter(name__contains=q)
        print("search_qs")
        print(search_qs)
        data = serializers.serialize('json', search_qs)
        data = json.loads(data)
        # city_names = [c['good_name'] for c in all_city_names if q in c["input_name"].lower()]
        # city_names = set(city_names) #removing duplicates
        # print("city_names")
        # print(city_names)
        results = []
        for control_element in data:
            ce_json = {'value': control_element}
            results.append(ce_json)
        print(results)
        data = json.dumps(results)

    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

# @task_view
def save_smt(request):
    """Save a statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
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

        # Track if we are creating a new statement
        new_statement = False
        #print(dict(request.POST))
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

        # Associate Statement and Producer Element
        # TODO Only associate if we have created new statement object.
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

        # Associate Statement and System's root_element
        # TODO Only associate if we have created new statement object.
        # print("** System.objects.get(pk=form_values['system_id']).root_element", System.objects.get(pk=form_values['system_id']).root_element)
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

        # Update ElementControl smts_updated to know when control element on system was recently updated
        try:
            print("Updating ElementControl smts_updated")
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
        {"status": "success", "message": statement_msg + " " + producer_element_msg + " " + statement_element_msg,
         "statement": serialized_obj})


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

        #print(dict(request.POST))
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
            return JsonResponse({"status": "error", "message": statement_msg})
        # Save Statement object
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


def search_system_component(request):
    """Add an existing element and its statements to a system"""
    print("searchhhh_system_component request")
    print(request)
    print(request.method)
    print("system_id")
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    print(dict(request.GET))
    form_dict = dict(request.GET)
    form_values = {}
    for key in form_dict.keys():
        form_values[key] = form_dict[key][0]
    # Form values from ajax data

    if "system_id" in form_values.keys():
        system_id = form_values['system_id']
        # TODO: get producer element id from system id and/or statement

        producer_element_id = form_values['producer_element_form_id'][0]#form_values['producer_element_id']
        # Does user have permission to add element?
        # Check user permissions
        system = System.objects.get(pk=system_id)
        print("system")
        print(system)
       #system = System.objects.get(pk=system_id)
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
        print("selected_controls_ids")
        print(selected_controls_ids)
        print("selected_controls")
        print(selected_controls)
        # Add element
        # Look up the element
        producer_element = Element.objects.get(pk=producer_element_id)
        print("producer_element")
        print(producer_element)
        # TODO: Handle case of element already associated with system

        cl_id =  form_values['control_id']#"ac-2"#oscalize_control_id(cl_id)
        text =  form_values['text']
        print("cl_id")
        print(cl_id)
        print("text")
        print(text)
        # The final elements that are returned to the new dropdown created...
        producer_system_elements = Element.objects.filter(element_type="system_element").filter(name__contains= text)
        print("producer_system_elements")
        print(producer_system_elements)

        # only prototype implementation statements for the given control
        #control_ids = Statement.objects.filter(statement_type="control_implementation_prototype").filter(sid=cl_id)
       # print("control_ids")
       # print(control_ids)
       #  for contorl_id in control_ids:
       #      filtered_by_element_name = Element.objects.filter(id=contorl_id.producer_element_id)
       #      # Element.objects.get(pk=producer_element_id)
       #      # filtered_by_element_name = Element.filter(name__contains= text)
       #      print("filtered_by_element_name")
       #      print(filtered_by_element_name)
        # Loop through element's prototype statements and add to control implementation statements
        #print("Adding {} to system_id {}".format(producer_element.name, system_id))
        # for smt in Statement.objects.filter(producer_element_id = producer_element.id, statement_type="control_implementation_prototype"):
        #     # Only add statements for controls selected for system
        #     if "{} {}".format(smt.sid, smt.sid_class) in selected_controls_ids:
        #         print("smt", smt)
        #         smt.create_instance_from_prototype(system.root_element.id)
        #     else:
        #         print("not adding smt not selected controls for system", smt)

        producer_elements = [{"id":str(ele.id), "name": ele.name} for ele in producer_system_elements]
        print("producer_elements")
        print(producer_elements)
        results = {'producer_element_name_value': producer_elements}
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    # # Redirect to selected element page
    # return HttpResponseRedirect("/systems/{}/components/selected".format(system_id))

def add_system_component(request, system_id):
    """Add an existing element and its statements to a system"""
    print("addinggggg_system_component request")
    print(request)
    print(request.method)
    print("system_id")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    print(dict(request.POST))
    form_dict = dict(request.POST)
    form_values = {}
    for key in form_dict.keys():
        form_values[key] = form_dict[key][0]
    # Form values from ajax data

    if "system_id" in form_values.keys():
        # This returns all the elements by system element and control id
        # for system_ele in producer_system_elements:
        #     filtered_by_element_name2 = Statement.objects.filter(sid=cl_id).filter(producer_element_id=system_ele)
        #     # Element.objects.get(pk=producer_element_id)
        #     # filtered_by_element_name = Element.filter(name__contains= text)
        #     print("filtered_by_element_name2")
        #     print(filtered_by_element_name2)


        system_id = form_values['system_id']
        producer_element_id = form_values['selected_producer_element_form_id']
        # Does user have permission to add element?
        # Check user permissions
        system = System.objects.get(pk=system_id)
        print("system")
        print(system)
       #system = System.objects.get(pk=system_id)
        if not request.user.has_perm('change_system', system):
            # User does not have write permissions
            # Log permission to save answer denied
            logger.info(
                event="change_system permission_denied",
                object={"object": "element", "entered_producer_element_name": form_values['text']},
                user={"id": request.user.id, "username": request.user.username}
            )
            return HttpResponseForbidden("Permission denied. {} does not have change privileges to system and/or project.".format(request.user.username))

        selected_controls = system.root_element.controls.all()
        selected_controls_ids = set()
        for sc in selected_controls:
            selected_controls_ids.add("{} {}".format(sc.oscal_ctl_id, sc.oscal_catalog_key))

        # Add element
        # Look up the element
        producer_element = Element.objects.get(pk=producer_element_id)
        # TODO: Handle case of element already associated with system

        # Loop through element's prototype statements and add to control implementation statements
        print("Adding {} to system_id {}".format(producer_element.name, system_id))
        for smt in Statement.objects.filter(producer_element_id = producer_element.id, statement_type="control_implementation_prototype"):
            # Only add statements for controls selected for system
            if "{} {}".format(smt.sid, smt.sid_class) in selected_controls_ids:
                print("smt", smt)
                smt.create_instance_from_prototype(system.root_element.id)
            else:
                print("not adding smt not selected controls for system", smt)

        results = [{'producer_element_name_value': producer_element.name}]
        data = json.dumps(results)
        mimetype = 'application/json'
        #return HttpResponse(data, mimetype)
    # Redirect to selected element page
   # return HttpResponse('systems/{}/controls/catalogs/{}/control/{}'.format(system_id, form_values['catalog_key'], form_values['control_id']))
    return HttpResponseRedirect("/systems/{}/components/selected".format(system_id))
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

    return HttpResponseRedirect("/systems/{}/controls/selected".format(system_id))


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
        # print(temp_dir.name)
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
    from .forms import StatementPoamForm, PoamForm
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
    from .forms import StatementPoamForm, PoamForm
    from django.shortcuts import get_object_or_404

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
