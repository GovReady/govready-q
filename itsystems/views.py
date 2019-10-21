from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django import forms
from django.forms import ModelForm
from itsystems.forms import SystemInstanceForm
from itsystems.forms import HostInstanceForm

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
    hostinstance  = HostInstance.objects.get(id=pk)
    return render(request, "itsystems/hostinstance.html", {
        "hostinstance": hostinstance,
        "agent": hostinstance.get_first_agent()
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
        return redirect('systeminstance_hostinstances_list', pk=hostinstance.pk)
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









