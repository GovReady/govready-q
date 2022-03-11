from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseNotFound
import requests
import argparse
import os
import importlib
from .utils.integration import Communication
from .models import Integration, Endpoint
from .csam.communicate import CSAMCommunication
from .github.communicate import GithubCommunication
from .jsonplaceholder.communicate import JsonplaceholderCommunication


def set_integration(integration):
    """Select correct integration"""

    if integration == "csam":
        return CSAMCommunication()
    elif integration == "github":
        return GithubCommunication()
    elif integration == "jsonplaceholder":
        return JsonplaceholderCommunication()
    else:
        return None

    # QUESTION: Is there a better way to make dynamic assignments?
    # CAN'T USE BELOW APPROACH BECAUSE IMPORT MODULES ONLY DONE ON FIRST INTERPRETATON
    # load correct module (directory path) for integration
    # path = f"integrations.{integration}.communicate"
    # check if path exists
    # import ipdb; ipdb.set_trace()
    # if not os.path.isdir(os.path.join(f"{os.path.sep}".join(path.split('.')[:-1]))):
    #     print(f"Path '{path}' to integration module {integration} does not exits")
        # raise error
    # importlib.invalidate_caches()
    # importlib.import_module(path)
    # load module's Communication subclass for integration
    # communication_classes = Communication.__subclasses__()
    # if not communication_classes:
    #     print(f"Unable to find class inheriting `Communication` in {path}")
        # report/raise error
    # import ipdb; ipdb.set_trace()
    # communication = communication_classes[0]()

def integration_identify(request, integration_name):
    """Integration returns an identification"""

    integration = get_object_or_404(Integration, name=integration_name)
    communication = set_integration(integration_name)
    if communication is None: return HttpResponseNotFound('<h1>404 - Integration not found.</h1>')
    identified = communication.identify()
    return HttpResponse(f"Attempting to communicate with '{integration_name}' integration: {identified}")

def integration_endpoint(request, integration_name, endpoint=None):
    """Communicate with an integrated service"""

    integration = get_object_or_404(Integration, name=integration_name)
    if integration is None: return HttpResponseNotFound(f'<h1>404 - Integration configuration not found.</h1>')
    communication = set_integration(integration_name)
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

def integration_endpoint_post(request, integration_name, endpoint=None):
    """Communicate with an integrated service using POST"""

    integration = get_object_or_404(Integration, name=integration_name)
    if integration is None: return HttpResponseNotFound(f'<h1>404 - Integration configuration not found.</h1>')
    communication = set_integration(integration_name)
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
