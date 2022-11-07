from django.shortcuts import render

import json
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

from guardian.core import ObjectPermissionChecker
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_perms_for_model, get_perms, assign_perm

from controls.models import System
from .models import WorkflowImage, WorkflowInstanceSet, WorkflowInstance, WorkflowRecipe
from .forms import WorkflowRecipeForm
from .factories import *

from siteapp.notifications_helpers import *

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


@login_required
def workflowrecipes_all(request):
    """List all workflow recipes"""

    workflowrecipes = WorkflowRecipe.objects.all().order_by("name")
    context = {
        "is_admin": request.user.is_superuser,
        "workflowrecipes": workflowrecipes,
    }
    return render(request, "workflow/recipes_all.html", context)

@login_required
def manage_recipe(request):
    context ={}
 
    form = WorkflowRecipeForm(request.POST or None, request.FILES or None) 
    if form.is_valid():
        workflowrecipe = form.save()
        # create related workflowimage
        fif = FlowImageFactory(workflowrecipe.name)
        workflowimage = fif.create_workflowimage_from_workflowrecipe(workflowrecipe)
        messages.add_message(request, messages.INFO, f"Workflow recipe \"{workflowrecipe.name}\" created.")
        # create related worflowinstanceset
        # create related orphan worflowinstance
        # workflowimage.create_orphan_worflowinstance(name=workflowrecipe.name)
        return redirect('workflowrecipes_all')
    context['form'] = form
    return render(request, "workflow/recipe_form.html", context)

@login_required
def edit_recipe(request, pk):

    workflowrecipe = get_object_or_404(WorkflowRecipe, pk=pk)
    form = WorkflowRecipeForm(request.POST or None, instance=workflowrecipe, initial={'workflowrecipe': workflowrecipe.id})
    if request.method == 'POST':
        try:
            form = WorkflowRecipeForm(request.POST, instance=workflowrecipe)
            if form.is_valid():
                form.save()
                # update related workflowimage
                fif = FlowImageFactory(workflowrecipe.name)
                print("[DEBUG] 1 workflowrecipe after form save:", workflowrecipe)
                workflowimage = fif.create_workflowimage_from_workflowrecipe(workflowrecipe)
                messages.add_message(request, messages.INFO, f"Workflow recipe \"{form.data['name']}\" updated.")
                return redirect("workflowrecipes_all")
        except:
            messages.add_message(request, messages.ERROR,
                                 f"Error. Workflow recipe \"{form.data['name']}\" update failed.")
    return render(request, 'workflow/recipe_form.html', {
        'form': form,
        'workflowrecipe': workflowrecipe,
    })

@login_required
@transaction.atomic
def delete_recipe(request, pk):
    """Form to delete recipes"""

    # import ipdb; ipdb.set_trace()
    if request.method == 'GET':
        workflowrecipe = get_object_or_404(WorkflowRecipe, pk=pk)
        try:
            if WorkflowImage.objects.filter(workflowrecipe=workflowrecipe).exists():
                WorkflowImage.objects.filter(workflowrecipe=workflowrecipe).delete()
            WorkflowRecipe.objects.get(pk=pk).delete()
            logger.info(
                event="delete_workflowrecipe",
                object={"object": "workflowrecipe", "id": workflowrecipe.id, "title": workflowrecipe.title},
                user={"id": request.user.id, "username": request.user.username}
            )

            messages.add_message(request, messages.INFO, f"Workflow recipe \"{workflowrecipe.name}\" deleted.")
            return redirect("workflowrecipes_all")
        except:
            logger.info(
                event="delete_workflowrecipe_failed",
                object={"object": "workflowrecipe", "id": workflowrecipe.id, "name": workflowrecipe.name},
                user={"id": request.user.id, "username": request.user.username},
                detail={"message": "Other error when running delete on workflowrecipe object."}
            )
            return redirect('workflowrecipes_all')

@login_required
def duplicate_recipe(request, pk):
    """Duplicate an existing Workflow recipe."""

    if request.method == 'GET':
        workflowrecipe = get_object_or_404(WorkflowRecipe, pk=pk)
        workflowrecipe.pk = None
        workflowrecipe.name = f"Copy of {workflowrecipe.name}"
        workflowrecipe.save()

        # create workflow image and instance for duplicate
        fif = FlowImageFactory(workflowrecipe.name)
        workflowimage = fif.create_workflowimage_from_workflowrecipe(workflowrecipe)
        workflowimage.create_orphan_worflowinstance(name=workflowimage.name)

        messages.add_message(request, messages.INFO, f"Workflow recipe \"{workflowrecipe.name}\" copied.")
        return redirect("workflowrecipes_all")

@login_required
def create_workflowimage(request, pk):
    """Create a workflow image from a workflow recipe"""

    workflowrecipe = get_object_or_404(WorkflowRecipe, pk=pk)
    # create workflow image and instance for duplicate
    fif = FlowImageFactory(workflowrecipe.name)
    workflowimage = fif.create_workflowimage_from_workflowrecipe(workflowrecipe)

    messages.add_message(request, messages.INFO, f"Workflow image \"{workflowimage.name}\" created.")
    redirect_url = f'/workflow/images/all'
    return HttpResponseRedirect(redirect_url)

@login_required
def delete_workflowimage(request, pk):
    """Form to delete recipes"""

    if request.method == 'GET':
        workflowimage = get_object_or_404(WorkflowImage, pk=pk)
        try:
            WorkflowImage.objects.get(pk=pk).delete()
            logger.info(
                event="delete_workflowimage",
                object={"object": "workflowimage", "id": workflowimage.id, "title": workflowimage.title},
                user={"id": request.user.id, "username": request.user.username}
            )
            messages.add_message(request, messages.INFO, f"Workflow image \"{workflowimage.name}\" deleted.")
            return redirect("workflowimages_all")
        except:
            logger.info(
                event="delete_workflowimage_failed",
                object={"object": "workflowimage", "id": workflowimage.id, "name": workflowimage.name},
                user={"id": request.user.id, "username": request.user.username},
                detail={"message": "Other error when running delete on workflowimage object."}
            )
            return redirect('workflowimages_all')

@login_required
def create_workflowrecipe_from_image(request, pk):
    """Create a workflow recipe from a workflow image"""

    workflowimage = get_object_or_404(WorkflowImage, pk=pk)
    workflowrecipe = workflowimage.create_workflowrecipe_from_image()
    messages.add_message(request, messages.INFO, f"Workflow recipe \"{workflowimage.name}\" created from image \"{workflowimage.name}\".")
    return redirect('workflowrecipes_all')

@login_required
def workflowimages_all(request):
    """List all workflow images"""

    workflowimages = WorkflowImage.objects.all()
    context = {
        "workflowimages": workflowimages,
    }
    return render(request, "workflow/images_all.html", context)

@login_required
def create_workflowinstance(request, pk):
    """Create a workflow instance from a workflow image"""
    workflowimage = get_object_or_404(WorkflowImage, pk=pk)
    workflowimage.create_orphan_worflowinstance(name=workflowimage.name)
    redirect_url = f'/workflow/instances/all'
    return HttpResponseRedirect(redirect_url)

@login_required
def create_workflowinstance_from_recipe(request, pk):
    """Create a workflow instance from a workflow recipe"""

    workflowrecipe = get_object_or_404(WorkflowRecipe, pk=pk)
    # get workflow image or create it
    if WorkflowImage.objects.filter(workflowrecipe=workflowrecipe):
        workflowimage = WorkflowImage.objects.filter(workflowrecipe=workflowrecipe)[0]
    else:
        # create workflow image and instance for duplicate
        fif = FlowImageFactory(workflowrecipe.name)
        workflowimage = fif.create_workflowimage_from_workflowrecipe(workflowrecipe)
    workflowimage.create_orphan_worflowinstance(name=workflowimage.name)
    redirect_url = f'/workflow/instances/all'
    return HttpResponseRedirect(redirect_url)

@login_required
@transaction.atomic
def set_workflowinstance_feature_completed(request, workflowinstance_id):
    """Advance workflowinstace"""

    workflowinstance = get_object_or_404(WorkflowInstance, id=workflowinstance_id)
    workflowinstance.set_curr_feature_completed(request.user)
    workflowinstance.save()
    workflowinstance.rule_proc_rules(request)
    workflowinstance.save()
    workflowinstance.advance_feature(request.user)
    workflowinstance.save()
    # return to referrer page that sent request
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def workflowinstances_all(request):
    """List all workflow instances"""
    
    workflowinstancesets = WorkflowInstanceSet.objects.all()
    system_workflowinstances = WorkflowInstance.objects.exclude(workflowinstanceset=None).order_by('name','id')
    orphan_workflowinstances = WorkflowInstance.objects.filter(workflowinstanceset=None).order_by('name','id')

    context = {
        "is_admin": request.user.is_superuser,
        "workflowinstancesets": workflowinstancesets,
        "system_workflowinstances": system_workflowinstances,
        "orphan_workflowinstances": orphan_workflowinstances,
    }
    return render(request, "workflow/all.html", context)

@login_required
def create_system_worflowinstances(request, pk):
    """Create a workflowinstances from a workflowimage and assign to all systems"""

    workflowimage = get_object_or_404(WorkflowImage, pk=pk)
    assign_filter = 'ALL'
    workflowimage.create_system_worflowinstances(assign_filter, name=workflowimage.name)
    if assign_filter == 'ALL':
        messages.add_message(request, messages.INFO, f"Workflow \"{workflowimage.name}\" assigned to systems.")
    # TODO: handle INCLUDE, EXCLUDE filters maybe
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def create_system_worflowinstances_from_recipe(request, pk):
    """Create a workflowinstances from a workflow recipe and assign to all systems"""

    workflowrecipe = get_object_or_404(WorkflowRecipe, pk=pk)
    # get workflow image or create it
    if WorkflowImage.objects.filter(workflowrecipe=workflowrecipe):
        workflowimage = WorkflowImage.objects.filter(workflowrecipe=workflowrecipe)[0]
    else:
        # create workflow image and instance for duplicate
        fif = FlowImageFactory(workflowrecipe.name)
        workflowimage = fif.create_workflowimage_from_workflowrecipe(workflowrecipe)

    # workflowimage = get_object_or_404(WorkflowImage, pk=pk)
    assign_filter = 'ALL'
    workflowimage.create_system_worflowinstances(assign_filter, name=workflowimage.name)
    if assign_filter == 'ALL':
        messages.add_message(request, messages.INFO, f"Workflow \"{workflowimage.name}\" assigned to systems.")
    # TODO: handle INCLUDE, EXCLUDE filters maybe
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
