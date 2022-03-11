from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseNotFound
from integrations.models import Integration, Endpoint
from .communicate import CSAMCommunication


def set_integration():
    """Select correct integration"""
    return CSAMCommunication()

def integration_identify(request):
    """Integration returns an identification"""

    communication = set_integration()
    if communication is None: return HttpResponseNotFound('<h1>404 - Integration not found.</h1>')
    identified = communication.identify()
    return HttpResponse(f"Attempting to communicate with csam integration: {identified}")

def integration_endpoint(request, integration_name='csam', endpoint=None):
    """Communicate with an integrated service"""

    integration = get_object_or_404(Integration, name=integration_name)
    if integration is None: return HttpResponseNotFound(f'<h1>404 - Integration configuration not found.</h1>')
    communication = set_integration()
    if communication is None: return HttpResponseNotFound(f'<h1>404 - Integration not found.</h1>')
    identified = communication.identify()
    data = communication.get_response(endpoint)

    # add results into Endpoint model
    ep, created = Endpoint.objects.update_or_create(
        integration=integration,
        endpoint_path=endpoint,
        data=data
    )

    return HttpResponse(f"Attempting to communicate with '{integration}' integration: {identified}. endpoint: {endpoint}. <br> Returned data: {data}")

def integration_endpoint_post(request, integration_name='csam', endpoint=None):
    """Communicate with an integrated service using POST"""

    integration = get_object_or_404(Integration, name=integration_name)
    if integration is None: return HttpResponseNotFound(f'<h1>404 - Integration configuration not found.</h1>')
    communication = set_integration()
    if communication is None: return HttpResponseNotFound(f'<h1>404 - Integration not found.</h1>')
    identified = communication.identify()
    data = communication.post_response(endpoint)

    # add results into Endpoint model

    ep, created = Endpoint.objects.update_or_create(
        integration=integration,
        endpoint_path=endpoint,
        data=data
    )

    return HttpResponse(f"Attempting to communicate using POST with '{integration}' integration: {identified}. endpoint: {endpoint}. <br> Returned data: {data}")
