from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django import forms
from django.forms import ModelForm
from itsystems.forms import SystemInstanceForm
from itsystems.forms import HostInstanceForm
import json

import re

from .models import SystemInstance, HostInstance, AgentService, Agent

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the itsystems index.")

@login_required
def systeminstance_list(request):
    """List system instances"""
    # TODO: Restrict to user's permissions
    return render(request, "itsystems/systeminstance_index.html", {
        "systeminstances": SystemInstance.objects.all(),
    })

@login_required
def hostinstance_list(request):
    """List host instances"""
    # TODO: Restrict to user's permissions
    return render(request, "itsystems/hostinstance_index.html", {
        "hostinstances": HostInstance.objects.all(),
    })

@login_required
def systeminstance_hostinstances_list(request, pk):
    """List system instance host intances"""
    # TODO: Restrict to user's permissions
    systeminstance  = SystemInstance.objects.get(id=pk)
    hostinstances = systeminstance.get_hostinstances()
    return render(request, "itsystems/systeminstance_hostinstances.html", {
        "systeminstance": systeminstance,
        "hostinstances": hostinstances,
    })

@login_required
def hostinstance(request, pk):
    """HostInstance detail"""
    # TODO: Restrict to user's permissions
    print("** hostinstance ** pk: {}".format(pk))
    try:
        hostinstance = HostInstance.objects.get(id=pk)
        print("* try works *")
    except:
        print("* try fails *")
        hostinstance = None
        # return HttpResponseNotFound("404 - page not found.")

    try:
        agent = hostinstance.get_first_agent()
    except:
        agent = None
        agent_service = None
        
    # Retrieving data from a service
    # MVP currently supports only Wazuh
    # Wazuh record must already exist in database AgentService table
    # Name: Wazuh
    # Api_user: <api_user_name>
    # Api_pw: <api_pw>
    # TODO: AgentService should be set by HostInstance - Agent relationship, yes?
    agent_service = AgentService.objects.filter(name='Wazuh').first()
    if agent_service:
        agent_service_api_address = "35.175.122.207:55000"
        agent_service_api_user = agent_service.api_user
        agent_service_api_pw = agent_service.api_pw
        
        import requests
        from requests.auth import HTTPBasicAuth
        r = requests.get('http://35.175.122.207:55000/summary/agents?pretty', auth=HTTPBasicAuth(agent_service_api_user, agent_service_api_pw))
        agent_service_data = r.json()
        agent_service_data_pretty = json.dumps(agent_service_data, sort_keys=True, indent=4)
    else:
        agent_service_data_pretty = "Agent Service not defined or not supported."

    return render(request, "itsystems/hostinstance.html", {
        "hostinstance": hostinstance,
        "agent": agent,
        "agent_service_data_pretty": agent_service_data_pretty
    })

@login_required
def new_systeminstance(request):
    """Form to create new system instances"""
    # return HttpResponse("This is for new system instance.")
    if request.method == 'POST':
      form = SystemInstanceForm(request.POST)
      if form.is_valid():
        form.save()
        systeminstance = form.instance
        # systeminstance.assign_owner_permissions(request.user)
        return redirect('systeminstance_hostinstances_list', pk=systeminstance.pk)
    else:
        form = SystemInstanceForm()

    return render(request, 'itsystems/systeminstance_form.html', {
        'form': form,
        "system_instance_form": SystemInstanceForm(request.user),
    })

@login_required
def new_hostinstance(request):
    """Form to create new system instances"""
    # return HttpResponse("This is for new host instance.")
    if request.method == 'POST':
      form = HostInstanceForm(request.POST)
      if form.is_valid():
        form.save()
        hostinstance = form.instance
        # systeminstance.assign_owner_permissions(request.user)
        return redirect('systeminstance_hostinstances_list', pk=hostinstance.system_instance.pk)
    else:
        form = HostInstanceForm()

    return render(request, 'itsystems/hostinstance_form.html', {
        'form': form,
        "host_instance_form": HostInstanceForm(request.user),
    })

@login_required
def new_agent(request):
    """Form to create new agent"""
    return HttpResponse("This is for new agent.")

@login_required
def new_agentservice(request):
    """Form to create new agent service"""
    return HttpResponse("This is for new agent service.")









