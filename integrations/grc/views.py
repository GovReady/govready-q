import json
import time
import importlib
import markdown
import logging
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from integrations.models import Integration, Endpoint
from .communicate import GRCCommunication
from controls.models import System, Element
from siteapp.models import Organization, Portfolio, Folder
from siteapp.views import get_compliance_apps_catalog_for_user, start_app
from guidedmodules.models import AppSource
from guidedmodules.app_loading import ModuleDefinitionError

logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


INTEGRATION_NAME = 'grc'
try:
    INTEGRATION = get_object_or_404(Integration, name=INTEGRATION_NAME)
except:
    HttpResponseNotFound(f'<h1>404 - Integration configuration missing. Create Integration database record.</h1>')

def set_integration():
    return GRCCommunication()

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
    try:
        # system = System.objects.get(pk=system_id)
        system = get_object_or_404(System, pk=system_id)
    except:
        return HttpResponse(
        f"<html><body>"
        f"<p>now: {datetime.now()}</p>"
        f"<p>System '{system_id}' does not exist.</p>"
        f"</body></html>")

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

def update_system_description(request, params={"src_obj_type": "system", "src_obj_id": 2}):
    """Update System description in CSAM"""

    system_id = params['src_obj_id']
    system = System.objects.get(pk=system_id)
    # TODO: Check user permission to update
    csam_system_id = system.info.get('csam_system_id', None)
    # print("10, ========== csam_system_id", csam_system_id)
    if csam_system_id is not None:
        new_description = "This is the new system description."
        endpoint = f"/v1/systems/{csam_system_id}"
        post_data = {
            "description": new_description
        }
        communication = set_integration()
        data = communication.post_response(endpoint, data=json.dumps(post_data))
        result = data
    return result

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
        # Redirect to the new system/project.
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

