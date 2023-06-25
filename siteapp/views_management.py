import subprocess #nosec
import sys

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.conf import settings
from django.core import management
#
import json
from secrets import compare_digest
from siteapp.models import User, Project, Organization
from django.views.decorators.csrf import csrf_exempt



def print_http_response(f):
    """
    Wraps a python function that prints to the console, and
    returns those results as a HttpResponse (HTML)
    """

    class WritableObject:
        def __init__(self):
            self.content = []
        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(['<BR>' if c == '\n' else c for c in printed.content ])
    return new_f


def index(request):
    html = (
        '<html><body>'
        '<h3>Call Django management commands</h3>'
        '<ul>'
        '<li><a href="/management/is_superuser">is_superuser</a> - check if user is_superuser</li>'
        '<li><a href="/management/listcomponents">manage.py listcomponents</a> - generate a list of components</li>'
        '<li><a href="/management/set_baseline_controls">manage.py set_baseline_controls</a> - set_baseline_controls --username user --baseline catalog:baseline --overlay privacy:moderate</li>'
        '<li><a href="/management/load_app_template">manage.py load_app_template</a> - load_app_template --username user --template path/template --project_name "System Security Plan"</li>'
        '</body></html>' )
    return HttpResponse(html)

def is_superuser(request):
    # output = subprocess.check_output(["./check-system.sh"]).decode("utf-8")
    html = f"<html><body><pre>is_superuser: {request.user.is_superuser}</pre></body></html>"
    return HttpResponse(html)

@csrf_exempt
@print_http_response
def listcomponents(request):
    if not request.user.is_superuser:
        html = f"<html><body><pre>Page only available to admins - won't be displayed because of decorator</pre></body></html>"
        return HttpResponse(html)

    # user is admin, run command
    result = management.call_command('listcomponents')
    html = f"<html><body><pre>manage.py listcomponents\n request.user.is_superuser: {request.user.is_superuser} {result}</pre></body></html>"
    return HttpResponse(html)

@csrf_exempt
@print_http_response
def set_baseline_controls(request, *args):
    try:
        payload     = request.body.decode("utf-8")
        params      = json.loads(payload)
        user        = params['username']
        baseline    = params['baseline']  # ToDo: multiple baselines
        system_name = params['project']
    except Exception as e:
        return HttpResponseForbidden( f"Missing parameters: {e}", content_type="text/plain",)

    try:
        project = Project.objects.filter(system__root_element__name=system_name).first()
        if project == None:
            raise Exception('Project not found')
    except Exception as e:
        return HttpResponseForbidden( f"Missing parameters: {e}", content_type="text/plain",)

    # Is user project member or is_superuser
    project_member = False
    members = User.objects.filter(projectmembership__project=project)
    for member in members:
        if member.username == user:
            project_member  = member.username
    try:
        user_id    = User.objects.get(username=user)
    except Exception as e:
        return HttpResponseForbidden( f"Forbidden: {e}", content_type="text/plain",)

    # Bail if any parameters missing
    try:
        if not (user and baseline and system_name and project and members and user_id):
            return HttpResponseForbidden( f"Forbidden: Missing parameters", content_type="text/plain",)
    except Exception as e:
        return HttpResponseForbidden(f"Forbidden: Missing parameters {e}", content_type="text/plain",)

    if ((project_member != user) and not (user_id.is_superuser)):
        return HttpResponseForbidden( f"Permission denied to user for project.", content_type="text/plain",)

    # Does the user_id.api_key_ro token in DB match
    # what was sent in the header for this user
    given_token = request.headers.get("CaC-Webhook-Auth-Token", "")
    user_id     = User.objects.get(username=params['username'])
    if not (compare_digest(given_token, user_id.api_key_wo)):
        return HttpResponseForbidden( "Incorrect token in CaC-Webhook-Auth-Token header.", content_type="text/plain",)

    # user is authorized, run command
    result = management.call_command('set_baseline_controls',username=user, baseline=baseline,project=project.title)
    html = f"<html><body><pre>manage.py set_baseline_controls\n request.user.is_superuser: {request.user} {result} with args {params} userid is superuser: {user_id.is_superuser} </pre></body></html>"
    return HttpResponse(html)

@csrf_exempt
@print_http_response
def load_app_template(request, *args):
    try:
        payload     = request.body.decode("utf-8")
        params      = json.loads(payload)
        user        = params['username']
        template    = params['template']
        system_name = params['project']
    except Exception as e:
        return HttpResponseForbidden( f"Missing parameters: {e}", content_type="text/plain",)

    try:
        exists_project = Project.objects.filter(system__root_element__name=system_name).first()
        if exists_project == None:
            project = system_name
        else:
            raise Exception('Project already exists')
    except Exception as e:
        return HttpResponseForbidden( f"Bad parameters for project: {e}", content_type="text/plain",)

    try:
        user_id    = User.objects.get(username=user)
    except Exception as e:
        return HttpResponseForbidden( f"Forbidden: {e}", content_type="text/plain",)

    # Bail if any parameters missing
    try:
        if not (user and template and system_name and project):
            return HttpResponseForbidden( f"Forbidden: Missing parameters", content_type="text/plain",)
    except Exception as e:
        return HttpResponseForbidden(f"Forbidden: Missing parameters {e}", content_type="text/plain",)

    # Bail if requesting user not a superuser or allowed service account
    if not ((user_id == 's-compliance') or (user_id.is_superuser)):
        return HttpResponseForbidden( f"Permission denied: cannot create project.", content_type="text/plain",)

    # Does the user_id.api_key_ro token in DB match
    # what was sent in the header for this user
    given_token = request.headers.get("CaC-Webhook-Auth-Token", "")
    user_id     = User.objects.get(username=params['username'])
    if not (compare_digest(given_token, user_id.api_key_wo)):
        return HttpResponseForbidden( "Incorrect token in CaC-Webhook-Auth-Token header.", content_type="text/plain",)

    # user is authorized, run command
    result = management.call_command('load_app_template',username=user, template=template, project_name=project)
    html = f"<html><body><pre>manage.py load_app_template\n request.user.is_superuser: {request.user} {result} with args {params} userid is superuser: {user_id.is_superuser} </pre></body></html>"
    return HttpResponse(html)

@csrf_exempt
@print_http_response
def load_component_from_library(request, *args):
    try:
        payload      = request.body.decode("utf-8")
        params       = json.loads(payload)
        user         = params['username']
        component    = params['component']
        project_name = params['project_name']
        debug        = params['debug']
    except Exception as e:
        return HttpResponseForbidden( f"Missing parameters: {e}", content_type="text/plain",)

    try:
        project = Project.objects.filter(system__root_element__name=project_name).first()
        if project == None:
            raise Exception('Project not found')
    except Exception as e:
        return HttpResponseForbidden( f"Missing parameters: {e}", content_type="text/plain",)

    # Is user project member or is_superuser
    project_member = False
    members = User.objects.filter(projectmembership__project=project)
    for member in members:
        if member.username == user:
            project_member  = member.username
    if not project_member:
        return HttpResponseForbidden( f"Exception: user not project member: {members}", content_type="text/plain",)
    if not project_member:
        raise Exception(user)
    try:
        user_id    = User.objects.get(username=user)
    except Exception as e:
        return HttpResponseForbidden( f"Forbidden: {e}", content_type="text/plain",)

    # Does component exist?
        try:
            producer_element = Element.objects.filter(name=component).first() # or [0]
            if producer_element == None:
                raise Exception(component)
        except Exception as e:
            return HttpResponseForbidden( f"Exception: component not found: {e}", content_type="text/plain",)

    # Bail if any parameters missing
    try:
        if not (user and component and project_name and project and members and user_id):
            return HttpResponseForbidden( f"Forbidden: Missing parameters", content_type="text/plain",)
    except Exception as e:
        return HttpResponseForbidden(f"Forbidden: Missing parameters {e}", content_type="text/plain",)

    if ((project_member != user) and not (user_id.is_superuser)):
        return HttpResponseForbidden( f"Permission denied to user for project.", content_type="text/plain",)

    # Does the user_id.api_key_ro token in DB match
    # what was sent in the header for this user
    given_token = request.headers.get("CaC-Webhook-Auth-Token", "")
    user_id     = User.objects.get(username=params['username'])
    if not (compare_digest(given_token, user_id.api_key_wo)):
        return HttpResponseForbidden( "Incorrect token in CaC-Webhook-Auth-Token header.", content_type="text/plain",)

    # user is authorized, run command
    result = management.call_command('load_component_from_library',username=user, component=component,project_name=project_name,debug=debug)
    html = f"<html><body><pre>manage.py load_component_from_library\n request.user.is_superuser: {request.user} {result} with args {params} userid is superuser: {user_id.is_superuser} </pre></body></html>"
    return HttpResponse(html)

@csrf_exempt
@print_http_response
def import_control_catalog(request, *args):
    try:
        payload      = request.body.decode("utf-8")
        params       = json.loads(payload)
        user         = params['username']
        catalog_key  = params['catalog_key']
        catalog_file = params['catalog_file']
        baseline     = params['baseline']
        debug        = params['debug']
    except Exception as e:
        return HttpResponseForbidden( f"Missing parameters: {e}", content_type="text/plain",)

    # Bail if any parameters missing
    try:
        if not (user and catalog_key and catalog_file and baseline):
            return HttpResponseForbidden( f"Forbidden: Missing parameters", content_type="text/plain",)
    except Exception as e:
        return HttpResponseForbidden(f"Forbidden: Missing parameters {e}", content_type="text/plain",)
    
    try:
        user_id    = User.objects.get(username=user)
    except Exception as e:
        return HttpResponseForbidden( f"Forbidden: {e}", content_type="text/plain",)

    # Bail if requesting user not a superuser or allowed service account
    if not ((user_id == 's-compliance') or (user_id.is_superuser)):
        return HttpResponseForbidden( f"Permission denied.", content_type="text/plain",)

    # Does the user_id.api_key_ro token in DB match
    # what was sent in the header for this user
    given_token = request.headers.get("CaC-Webhook-Auth-Token", "")
    user_id     = User.objects.get(username=params['username'])
    if not (compare_digest(given_token, user_id.api_key_wo)):
        return HttpResponseForbidden( "Incorrect token in CaC-Webhook-Auth-Token header.", content_type="text/plain",)
    
    try:
        for cf in (catalog_file, baseline):
            # It's json, but is it really a catalog?
            is_json = json.dumps(cf)
            if not is_json:
                raise Exception(f'{is_json}')
    except Exception as e:
            print(f'Catalog Parsing Exception: {e}')

    # user is authorized, run command
    result = management.call_command('import_control_catalog',catalog_key=catalog_key, catalog_file=catalog_file, baseline=baseline)
    html = f"<html><body><pre>manage.py import_control_catalog\n request.user.is_superuser: {request.user} {result} with args {params} userid is superuser: {user_id.is_superuser} </pre></body></html>"
    # (OLD VERSION) html = f"<html><body><pre>manage.py listcomponents\n request.user.is_superuser: 333{request.user.is_superuser} {result}</pre></body></html>"
    return HttpResponse(html)
