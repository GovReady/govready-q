from django.shortcuts import render

import json
from datetime import datetime

from django.contrib.auth.models import Permission
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse

from guardian.core import ObjectPermissionChecker
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_perms_for_model, get_perms, assign_perm

from controls.models import System
from .models import WorkflowImage, WorkflowInstanceSet, WorkflowInstance

from siteapp.notifications_helpers import *

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


# Create your views here.
def set_workflowinstance_feature_completed(request, workflowinstance_id):
    """Advance workflowinstace"""

    workflowinstance = get_object_or_404(WorkflowInstance, id=workflowinstance_id)
    workflowinstance.set_curr_feature_completed(request.user)
    workflowinstance.advance(request.user)

    # temp hardcode return to system poa&m workflow
    # TODO: make return to system dynamic
    system_id = workflowinstance.system.id
    # redirect_url = request.session.get("_post_banner_url", "/")
    redirect_url = f'/systems/{system_id}/poams'
    return HttpResponseRedirect(redirect_url)

def workflowinstances_all(request):
    """List all workflow instances"""
    
    workflowinstancesets = WorkflowInstanceSet.objects.all()
     # redirect_url = f'/systems/139/poams'
    # return HttpResponseRedirect(redirect_url)
    # HttpResponse("workflowinstanceset")
    context = {
        "workflowinstancesets": workflowinstancesets,
    }
    return render(request, "workflow/all.html", context)
