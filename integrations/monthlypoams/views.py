from hashlib import new
import json
import time
import importlib
import markdown
import logging
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from integrations import monthlypoams
from integrations.models import Integration, Endpoint
from .communicate import MonthlyPOAMsCommunication
from controls.models import System, Element, Poam
# from controls.utilities import *
from siteapp.models import Organization, Portfolio, Folder
from siteapp.utils.views_helper import project_context, start_app, get_compliance_apps_catalog, \
    get_compliance_apps_catalog_for_user, get_compliance_apps_catalog_for_user
from guidedmodules.models import AppSource
from guidedmodules.app_loading import ModuleDefinitionError
import xlsxwriter

logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


INTEGRATION_NAME = 'monthlypoams'
try:
    INTEGRATION = get_object_or_404(Integration, name=INTEGRATION_NAME)
except:
    HttpResponseNotFound(f'<h1>404 - Integration configuration missing. Create Integration database record.</h1>')

# Add templates
import os
# from siteapp import settings
from django.conf import settings
# file = '/usr/src/app/integrations/__init__.py'
# settings.TEMPLATES[0]['DIRS'].append(os.path.join(os.path.dirname(file), 'monthlypoams','templates'))
# print(f"[DEBUG] updated TEMPLATES: ", settings.TEMPLATES[0]['DIRS'])
# settings.INSTALLED_APPS.append('monthlypoams')

def set_integration():
    return MonthlyPOAMsCommunication()

@login_required
@transaction.atomic
def integration_identify(request):
    """Integration returns an identification"""

    from django.urls import reverse
    communication = set_integration()
    url_patterns = getattr(importlib.import_module(f'integrations.{INTEGRATION_NAME}.urls'), "urlpatterns")
    url_routes = []
    for up in url_patterns:
        try:
            resolved_url = reverse(up.name)
        except:
            # hack to approximate reverse url path
            url_match_part = str(up.pattern.regex).replace('re.compile','').replace("('^","").replace("$'","")
            resolved_url = f"/integrations/{INTEGRATION_NAME}/{url_match_part}"
        up_dict = {
            "integration_name": INTEGRATION_NAME,
            "name": up.name,
            "url": resolved_url,
            # "importlib": f"importlib.import_module('integrations.{INTEGRATION_NAME}.views.{up.name}')"
        }
        url_routes.append(up_dict)

    # Retrieve README
    with open(f'integrations/{INTEGRATION_NAME}/README.md', 'r') as f:
        readme_markdown = f.readlines()
        readme_html = markdown.markdown("\n".join(readme_markdown))

    return render(request, "integrations/integration_detail.html", {
        "integration": communication.identify(),
        "integration_record": Integration.objects.get(name=INTEGRATION_NAME),
        "integration_name": INTEGRATION_NAME,
        "url_routes": url_routes,
        "readme_html": readme_html,
    })

@login_required
@transaction.atomic
def integration_endpoint(request, endpoint=None):
    """Communicate with an integrated service"""

    communication = set_integration()
    data = communication.get_response(endpoint)
    # Cache remote data locally in database
    ep, created = Endpoint.objects.get_or_create(
        integration=INTEGRATION,
        endpoint_path=endpoint
    )
    ep.data = data
    ep.save()

    return HttpResponse(
        f"<html><body><p>Attempting to communicate with '{INTEGRATION_NAME}' "
        f"integration: {communication.identify()}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>endpoint: {endpoint}</p>"
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(data,indent=4)}</pre>"
        f"</body></html>")

@login_required
@transaction.atomic
def integration_endpoint_post(request, endpoint=None):
    """Communicate with an integrated service using POST"""

    post_data = {
        "name": "My IT System2",
        "description":  "This is a more complex test system"
    }
    communication = set_integration()
    data = communication.post_response(endpoint, data=json.dumps(post_data))
    # Cache remote data locally in database
    ep, created = Endpoint.objects.get_or_create(
        integration=INTEGRATION,
        endpoint_path=endpoint
    )
    ep.data = data
    ep.save()

    return HttpResponse(
        f"<html><body><p>Attempting to communicate using POST with '{INTEGRATION_NAME}' "
        f"integration: {communication.identify()}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>endpoint: {endpoint}.</p>"
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(data,indent=4)}</pre>"
        f"</body></html>")

@login_required
@transaction.atomic
def monthly_poams_admin(request):
    """Administration screen for Monthly POA&Ms review"""

    from django.urls import reverse
    communication = set_integration()
    # url_patterns = getattr(importlib.import_module(f'integrations.{INTEGRATION_NAME}.urls'), "urlpatterns")
    # url_routes = []
    # for up in url_patterns:
    #     try:
    #         resolved_url = reverse(up.name)
    #     except:
    #         # hack to approximate reverse url path
    #         url_match_part = str(up.pattern.regex).replace('re.compile','').replace("('^","").replace("$'","")
    #         resolved_url = f"/integrations/{INTEGRATION_NAME}/{url_match_part}"
    #     up_dict = {
    #         "integration_name": INTEGRATION_NAME,
    #         "name": up.name,
    #         "url": resolved_url,
    #         # "importlib": f"importlib.import_module('integrations.{INTEGRATION_NAME}.views.{up.name}')"
    #     }
    #     url_routes.append(up_dict)

    # Retrieve README
    with open(f'integrations/{INTEGRATION_NAME}/README.md', 'r') as f:
        readme_markdown = f.readlines()
        readme_html = markdown.markdown("\n".join(readme_markdown))

    # return render(request, "monthlypoams2/system.html", {
    return render(request, "monthlypoams/monthly_poams_admin.html", {
        "integration": communication.identify(),
        "integration_record": Integration.objects.get(name=INTEGRATION_NAME),
        "integration_name": INTEGRATION_NAME,
        # "url_routes": url_routes,
        "readme_html": readme_html,
    })

@login_required
@transaction.atomic
def export_csam_poams_xlsx(request):
    """Export poams to CSAM spreadsheet format"""

    # Save to spreadsheet
    def save_worksheet(poams_list, filename, custom_fields=None):
        """Save poams list to spreadsheet"""

        # print(f"saving {len(poams_list)} POAMS to file '{filename}'")
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        column_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#6487DC'})
        date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})
        # Write Column Headers
        headers = [
            "CSAM ID", 
            "Org", 
            "Sub Org", 
            "System Name", 
            "Acronym", 
            "System Category", 
            "System Operational Status", 
            "System Type", 
            "Contractor System", 
            "Financial System", 
            "FISMA Reportable", 
            "Critical Infrastructure", 
            "Mission Critical", 
            "UII Code", 
            "Investment Name", 
            "Portfolio", 
            "POAM ID", 
            "POAM Sequence", 
            "POAM Title", 
            "Detailed Weakness Description", 
            "Create Date", 
            "Days Since Creation", 
            "Scheduled Completion Date", 
            "Planned Start Date", 
            "Actual Start Date" , 
            "Planned Finish Date", 
            "Actual Finish Date", 
            "Status", 
            "Weakness",
            "Cost", 
            "Control Risk Severity", 
            "User Identified Criticality",
            "Severity", 
            "Workflow Status", 
            "Workflow Status Date", 
            "Days Until Auto-Approved",
            "Exclude From OMB",
            "Accepted Risk",
            "Assigned To",
            "Phone",
            "Email",
            "Assigned Date",
            "Delay Reason",
            "Controls",
            "CSFFunction",
            "CSFCategory",
            "CSFSubCategory",
            "Number Milestones",
            "Number Artifacts",
            "RBD Approval Date",
            "Deficiency Category",
            "Source of Finding",
            "Percent Complete",
            "Date % Complete Last Updated",
            "Delay Justification",
            "Monthly Status", 
            "Comments"
        ]
        # include custom fields
        # if custom_fields:
        #     for cf in custom_fields:
        #         headers.append(cf['field_name'])
        col_index = 0
        row_index = 0
        # write headers
        for col_index in range(0,len(headers)):
            worksheet.write(row_index, col_index, headers[col_index])
        # write content for each poam
        for index, poam in enumerate(poams_list):
            row_index = index + 1
            
            # Get Info from System
            
            ele = poam.statement.consumer_element
            sys = System.objects.get(root_element=ele)
            worksheet.write(row_index, headers.index("System Name"), ele.name)
            # for field in poam.keys():
            
            # 
            # Check for specific poam fields: 
            # poam_id => POAM ID
            worksheet.write(row_index, headers.index("POAM ID"), poam.poam_id) 
            # weakness => POAM Title
            worksheet.write(row_index, headers.index("POAM Title"), poam.weakness_name) 
            # controls => Controls
            worksheet.write(row_index, headers.index("Controls"), poam.controls)
            # scheduled_completion_date => Planned Finish Date
            worksheet.write(row_index, headers.index("Planned Finish Date"), poam.scheduled_completion_date.strftime('%x %X'))
            # milestones => Number Milestones
            worksheet.write(row_index, headers.index("Number Milestones"), poam.milestones)
            
            # Check POAM Statement for specific fields:
            # body => Detailed Weakness Description
            worksheet.write(row_index, headers.index("Detailed Weakness Description"), poam.statement.body)
            # status => Status
            worksheet.write(row_index, headers.index("Status"), poam.statement.status)
            # created => Create Date
            worksheet.write(row_index, headers.index("Create Date"), poam.created.strftime('%x %X'))
            
            # check if "poam extra" is in the list of headers, if it is, add it to the row
            for field in headers:
                col_index = headers.index(field)
                if sys.info.get(field) or sys.info.get(field) == 0:
                    sys_field = sys.info.get(field)
                    worksheet.write(row_index, col_index, str(sys_field).strip(":") ) 
                if poam.extra.get(field) or poam.extra.get(field) == 0:
                    poam_field = poam.extra.get(field)
                    worksheet.write(row_index, col_index, str(poam_field).strip(":") ) 

        # set column widths
        word_width = 20
        worksheet.set_column(1, 7, word_width)  # Width of columns B:H
        worksheet.set_column(3, 3, word_width * 2)  # Width of columns D
        worksheet.set_column(9, 9, word_width)  # Width of columns J
        worksheet.set_column(15, 15, word_width)  # Width of columns P
        worksheet.set_column(18, 19, word_width * 2)  # Width of columns S:T
        worksheet.set_column(20, 28, word_width)  # Width of columns U:AC
        worksheet.set_column(32, 35, word_width)  # Width of columns AG:AJ
        worksheet.set_column(38, 42, word_width)  # Width of columns AM:AQ
        worksheet.set_column(51, 51, word_width * 2)  # Width of columns AZ
        # close and save workbook
        workbook.close()
        return filename

    # get all POA&Ms
    # TODO: 
    #   - How to get only the POA&Ms from current month?
    #   - Erase saved file; make file file temporary directory
    poams_list = Poam.objects.all()
    # put all POA&Ms into spreadsheet
    file_name = f"poams_list_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.xlsx"
    save_worksheet(poams_list, file_name)
    # path = open(poams_xlsx_filepath, 'rb')
    path = open(f'{file_name}', 'rb')
    response = HttpResponse(path, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # mimetype is replaced by content_type for django 1.7
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    # remove created file
    return response


def get_system_info(request, system_id=2):
    """Retrieve the system information from CSAM"""

    # system = System.objects.get(pk=system_id)
    system = get_object_or_404(System, pk=system_id)
    # TODO: Check user permission to view
    csam_system_id = system.info.get('csam_system_id', None)
    if csam_system_id is None:
        return HttpResponse(
        f"<html><body><p>Attempting to communicate with '{INTEGRATION_NAME}' "
        f"integration: {communication.identify()}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>System '{system_id}' does not have an associated 'csam_system_id'.</p>"
        f"</body></html>")

    endpoint = f'/v1/systems/{csam_system_id}'
    communication = set_integration()
    data = communication.get_response(endpoint)
    # Cache remote data locally in database
    ep, created = Endpoint.objects.get_or_create(
        integration=INTEGRATION,
        endpoint_path=endpoint
    )
    ep.data = data
    ep.save()

    return HttpResponse(
        f"<html><body><p>Attempting to communicate with '{INTEGRATION_NAME}' "
        f"integration: {communication.identify()}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>endpoint: {endpoint}</p>"
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(data,indent=4)}</pre>"
        f"</body></html>")

def get_paired_remote_system_info_using_local_system_id(request, system_id=2):
    """Retrieve the system information from CSAM"""

    system = get_object_or_404(System, pk=system_id)
    # try:
    #     # system = System.objects.get(pk=system_id)
    #     system = get_object_or_404(System, pk=system_id)
    # except:
    #     return HttpResponse(
    #     f"<html><body>"
    #     f"<p>now: {datetime.now()}</p>"
    #     f"<p>System '{system_id}' does not exist.</p>"
    #     f"</body></html>")

    # TODO: Check user permission to view
    communication = set_integration()
    csam_system_id = system.info.get('csam_system_id', None)
    if csam_system_id is None:
        return HttpResponse(
        f"<html><body><p>Attempting to communicate with '{INTEGRATION_NAME}' "
        f"integration: {communication.identify()}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>System '{system_id}' does not have an associated 'csam_system_id'.</p>"
        f"</body></html>")

    endpoint = f'/v1/systems/{csam_system_id}'
    # is there local information?
    ep, created = Endpoint.objects.get_or_create(
        integration=INTEGRATION,
        endpoint_path=endpoint
    )
    data = communication.get_response(endpoint)
    # Cache remote data locally in database
    ep.data = data
    ep.save()

    context = {
        "integration_name": INTEGRATION_NAME,
        "system": system,
        "cached": True,
        "communication": communication,
        "ep": ep
    }
    from siteapp import settings
    # settings.TEMPLATES[0]['DIRS'].append('/Users/gregelinadmin/Documents/workspace/govready-q-private/integrations/csam/templates/')
    # print(2,"========= TEMPLATES", settings.TEMPLATES[0]['DIRS'])
    return render(request, "csam/system.html", context)

def get_multiple_system_info(request, system_id_list="1,2"):
    """Get and cach system info for multiple systems"""
    systems_updated = []
    systems = System.objects.filter(pk__in=system_id_list.split(","))
    for s in systems:
        csam_system_id = s.info.get("csam_system_id", None)
        if csam_system_id is None:
            print(f"System id {s.id} has no csam_system_id")
        else:
            endpoint = f'/v1/systems/{csam_system_id}'
            communication = set_integration()
            data = communication.get_response(endpoint)
            # Cache remote data locally in database
            ep, created = Endpoint.objects.get_or_create(
                integration=INTEGRATION,
                endpoint_path=endpoint
            )
            ep.data = data
            ep.save()
            msg = f"System id {s.id} info updated from csam system {csam_system_id}"
            print(msg)
            systems_updated.append(msg)
            time.sleep(0.25)

    return HttpResponse(
        f"<html><body><p>Attempting to communicate with '{INTEGRATION_NAME}' "
        f"get_multiple_system_info for system ids {system_id_list}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>Result:</p>"
        f"<pre>{systems_updated}</pre>"
        f"</body></html>")

def update_system_description_test(request, system_id=2):
    """Test updating system description in CSAM"""

    params={"src_obj_type": "system", "src_obj_id": system_id}
    data = update_system_description(params)
    return HttpResponse(
        f"<html><body><p>Attempting to update CSAM description of System id {system_id}...' "
        f"<p>now: {datetime.now()}</p>"
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(data,indent=4)}</pre>"
        f"</body></html>")

def update_system_description(request):
    """Update System description in CSAM"""

    system_id = request.POST.get('system_id')
    system = System.objects.get(pk=system_id)
    # TODO: Check user permission to update
    csam_system_id = system.info.get('csam_system_id', None)

    # get local system info
    # local_system_description = "This is the new system description."
    local_system_description = system.info.get('system_description', "")

    if csam_system_id is not None:
        endpoint = f"/v1/systems/{csam_system_id}"
        # Retrieve schema for endpoint
        # Post change data
        post_data = {
            "purpose": local_system_description
        }
        communication = set_integration()
        data = communication.post_response(endpoint, data=json.dumps(post_data))
        # result = data
    return HttpResponse(
        f"<html><body><p>Update sent to {INTEGRATION_NAME} for remote system id {system_id}."
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(data,indent=4)}</pre>"
        f"</body></html>")

def match_system_from_remote(request, remote_system_id):
    """Match a system in GovReady-Q based on info from integrated service"""

    print("Match a system in GovReady-Q based on info from integrated service")

    communication = set_integration()
    csam_system_id = int(remote_system_id)
    endpoint = f'/v1/systems/{csam_system_id}'
    # is there local information?
    ep, created = Endpoint.objects.get_or_create(
        integration=INTEGRATION,
        endpoint_path=endpoint
    )
    # TODO: Refresh data if empty
    if created:
        # Cache not available
        data = communication.get_response(endpoint)
        # Cache remote data locally in database
        ep.data = data
        ep.save()
    else:
        # Cache available
        cached = True
        pass
    # Check if remote_system_name matches name of a system in GovReady-Q
    if System.objects.filter(Q(root_element__name=ep.data['name'])).exists():
        #name matches
        matched_systems = System.objects.filter(Q(root_element__name=ep.data['name']))
        if len(matched_systems) == 1:
            matched_system = matched_systems[0]
            if matched_system.info == {}:
                matched_system.info = {"csam_system_id": csam_system_id }
                matched_system.save()
                msg = f"Matched existing System {matched_system.id} in GovReady based on CSAM system name {ep.data['name']}."
            else:
                msg = f"System {matched_system.id} in GovReady already matched to CSAM system id for \"{ep.data['name']}\"."
        else:
            msg = f"More than one system in GovReady matched to CSAM system name \"{ep.data['name']}\"."
    else:
        msg = f"No system in GovReady matched to CSAM system id {csam_system_id}."
    return HttpResponse(
        f"<html><body><p>{msg}</p>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(ep.data,indent=4)}</pre>"
        f"</body></html>")

def create_system_from_remote(request):
    """Create a system in GovReady-Q based on info from integrated service"""

    communication = set_integration()
    print("request", request.GET)
    remote_system_id = request.GET.get("remote_system_id_field", None)

    if remote_system_id is None:
        msg = "No remote system id received."
        data = {}
        return HttpResponse(
            f"<html><body><p>{msg}</p>"
            f"<p>Returned data:</p>"
            f"<pre>{json.dumps(data,indent=4)}</pre>"
            f"</body></html>")

    csam_system_id = int(remote_system_id)
    endpoint = f'/v1/systems/{csam_system_id}'
    # is there local information?
    ep, created = Endpoint.objects.get_or_create(
        integration=INTEGRATION,
        endpoint_path=endpoint
    )
    if created:
        data = communication.get_response(f"{endpoint}")
        ep.data = data
        if len(data.keys()) < 2:
            messages.add_message(request, messages.INFO, f"Failed to get data from {INTEGRATION_NAME} for system id {csam_system_id}. Reply was '{data}' ")
            return HttpResponseRedirect(f"/integrations/{INTEGRATION_NAME}")
        ep.save()
    else:
        # In future, we may want to handle differently if data already stored locally
        data = communication.get_response(f"{endpoint}")
        ep.data = data
        if len(data.keys()) < 2:
            messages.add_message(request, messages.INFO, f"Failed to get data from {INTEGRATION_NAME} for system id {csam_system_id}. Reply was \"{data}\" ")
            return HttpResponseRedirect(f"/integrations/{INTEGRATION_NAME}")
        ep.save()

    # Check if system aleady exists with csam_system_id
    if not System.objects.filter(Q(info__contains={"csam_system_id": csam_system_id})).exists():
        # Create new system
        # What is default template?
        source_slug = "govready-q-files-startpack"
        app_name = "speedyssp"
        # can user start the app?
        # Is this a module the user has access to? The app store
        # does some authz based on the organization.
        catalog = get_compliance_apps_catalog_for_user(request.user)
        for app_catalog_info in catalog:
            if app_catalog_info["key"] == source_slug + "/" + app_name:
                # We found it.
                break
        else:
            raise Http404()
        # Start the most recent version of the app.
        appver = app_catalog_info["versions"][0]
        organization = Organization.objects.first()  # temporary
        default_folder_name = "Started Apps"
        folder = Folder.objects.filter(
            organization=organization,
            admin_users=request.user,
            title=default_folder_name,
        ).first()
        if not folder:
            folder = Folder.objects.create(organization=organization, title=default_folder_name)
            folder.admin_users.add(request.user)
        task = None
        q = None
        # Get portfolio project should be included in.
        if request.GET.get("portfolio"):
            portfolio = Portfolio.objects.get(id=request.GET.get("portfolio"))
        else:
            if not request.user.default_portfolio:
                request.user.create_default_portfolio_if_missing()
            portfolio = request.user.default_portfolio
        # import ipdb; ipdb.set_trace()
        try:
            project = start_app(appver, organization, request.user, folder, task, q, portfolio)
        except ModuleDefinitionError as e:
            error = str(e)
        # Associate System with CSAM system
        new_system = project.system 
        new_system.info = {
            "csam_system_id": csam_system_id,
            "system_description": ep.data.get('purpose', '')
        }
        new_system.save()
        # Update System name to CSAM system name
        nsre = new_system.root_element
        # Make sure system root element name is unique
        name_suffix = ""
        while Element.objects.filter(name=f"{ep.data['name']}{name_suffix}").exists():
            # Element exists with that name
            if name_suffix == "":
                name_suffix = 1
            else:
                name_suffix = str(int(name_suffix)+1)
        if name_suffix == "":
            nsre.name = ep.data['name']
        else:
            nsre.name = f"{ep.data['name']}{name_suffix}"
        nsre.save()
        # Update System Project title to CSAM system name
        prt = project.root_task
        prt.title_override = nsre.name
        prt.save()
        logger.info(event=f"create_system_from_remote remote_service {INTEGRATION_NAME} remote_system_id {csam_system_id}",
                object={"object": "system", "id": new_system.id},
                user={"id": request.user.id, "username": request.user.username})
        messages.add_message(request, messages.INFO, f"Created new System in GovReady based on {INTEGRATION_NAME} system id {csam_system_id}.")

        # Redirect to the new system/project.
        return HttpResponseRedirect(project.get_absolute_url())
        # return redirect(reverse('system_summary', args=[new_system.id]))
    else:
        systems = System.objects.filter(Q(info__contains={"csam_system_id": csam_system_id}))
        if len(systems) == 1:
            system = systems[0]
            # Assume one project per system
            project = system.projects.all()[0]
            msg = f"System \"{project.title}\" already exists locally based on CSAM system id {csam_system_id}."
        else:
            project = None
            msg = f"Multiple systems aleady exists in GovReady based on CSAM system id {csam_system_id}."
            msg = msg + f"They are: " + ",".join(str(systems))
        messages.add_message(request, messages.INFO, f"{msg}")
        return HttpResponseRedirect(f"/integrations/{INTEGRATION_NAME}")

