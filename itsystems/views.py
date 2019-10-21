from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

import re

from .models import SystemInstance, HostInstance, AgentService, Agent

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the itsystems index.")

@login_required
def systeminstance_list(request):
    """List system instances"""
    # TODO: Restrict to user's permissions
    return render(request, "itsystems/index.html", {
        "systeminstances": SystemInstance.objects.all(),
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
