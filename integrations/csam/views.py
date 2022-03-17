import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseNotFound
from integrations.models import Integration, Endpoint
from .communicate import CSAMCommunication
from controls.models import System

INTEGRATION_NAME = 'csam'
try:
    INTEGRATION = get_object_or_404(Integration, name=INTEGRATION_NAME)
except:
    HttpResponseNotFound(f'<h1>404 - Integration configuration missing. Create Integration database record.</h1>')

def set_integration():
    return CSAMCommunication()

def integration_identify(request):
    """Integration returns an identification"""

    communication = set_integration()
    return HttpResponse(f"Attempting to communicate with csam integration: {communication.identify()}")

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
        f"<p>endpoint: {endpoint}.</p>"
        f"<p>Returned data:</p>"
        f"<pre>{json.dumps(data,indent=4)}</pre>"
        f"</body></html>")

def update_system_description_test(request, system_id=2):
    """Test updating system description in CSAM"""

    params={"src_obj_type": "system", "src_obj_id": system_id}
    data = update_system_description(params)
    return HttpResponse(
        f"<html><body><p>Attempting to update CSAM description of System id {system_id}...' "
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
        endpoint = f"/system/{csam_system_id}"
        post_data = {
            "description": new_description
        }
        communication = set_integration()
        data = communication.post_response(endpoint, data=json.dumps(post_data))
        result = data
    return result

