from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import requests
import argparse
import os
import importlib
from .utils.integration import Communication
# from .models import Endpoint
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


# def jsonplaceholders_users(request):
#     #pull data from third party rest api
#     print(1,"========", "view_users")
#     endpoint_name = 'Test API Jsonplaceholder'
#     endpoint_url = 'https://jsonplaceholder.typicode.com/users'
#     endpoint_description = 'Sample json results listing users'
    
#     from integrations.jsonplaceholder.communicate import JsonplaceholderCommunication
#     comms = JsonplaceholderCommunication()
#     users = comms.get_response(endpoint_url)

#     # response = requests.get(endpoint_url)
#     # convert reponse data into json
#     # users = response.json()
#     print(users)
#     return HttpResponse(users)

#     # add results into Endpoint model
#     # ep, created = Endpoint.objects.update_or_create(
#     #     name=endpoint_name, 
#     #     url=endpoint_url,
#     #     description=endpoint_description,
#     #     api_data=users
#     # )

#     # return render(request, "api_client/users.html", {"users": users})
#     pass

def integration_identify(request, integration):
    """Integration returns an identification"""

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

    communication = set_integration(integration)
    if communication is None: return HttpResponseNotFound('<h1>404 - Integration not found.</h1>')
    identified = communication.identify()
    return HttpResponse(f"Attempting to communicate with '{integration}' integration: {identified}")

def integration_endpoint(request, integration, endpoint=None):
    """Communicate with an integrated service"""

    communication = set_integration(integration)
    if communication is None: return HttpResponseNotFound('<h1>404 - Integration not found.</h1>')
    identified = communication.identify()
    data = communication.get_response(endpoint)

    return HttpResponse(f"Attempting to communicate with '{integration}' integration: {identified}. endpoint: {endpoint}. <br> Returned data: {data}")

