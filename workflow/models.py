from pathlib import Path
import os
import json
import auto_prefetch
from django.db import models
from django.db.models import Count
from django.utils.functional import cached_property
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)
from simple_history.models import HistoricalRecords
from jsonfield import JSONField
from natsort import natsorted

from api.base.models import BaseModel
from controls.models import System
from siteapp.model_mixins.tags import TagModelMixin
from controls.utilities import *

import uuid
import tools.diff_match_patch.python3 as dmp_module
from copy import deepcopy
from django.db import transaction
from django.core.validators import RegexValidator
from django.core.validators import validate_email

# Create your models here.
class WorkflowImage(auto_prefetch.Model, TagModelMixin, BaseModel):
    name = models.CharField(max_length=100, help_text="Descriptive name", unique=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier")
    workflow = models.JSONField(blank=True, default=dict, help_text="Workflow object")
    rules = models.JSONField(blank=True, default=dict, help_text="Rules object")

    def __str__(self):
        return f'<WorkflowImage name="{self.name}" id={self.id}>'

    def __repr__(self):
        # For debugging.
        return f'<WorkflowImage name="{self.name}" id={self.id}>'

    def create_workflowinstance_obj(self):
        """Returns a generic workflowinstance unsaved object from workflowimage"""
        wfinstance = WorkflowInstance()
        wfinstance.workflowimage = self
        wfinstance.name = self.name
        wfinstance.workflow = self.workflow
        wfinstance.rules = self.rules
        # add tag
        return wfinstance

    @transaction.atomic
    def create_system_worflowinstances(self, filter, system_id_list=[], name=None, description=None):
        """Create workflowinstances associated with systems as per filter
            @filter (str) - ALL | INCLUDE | EXCLUDE
            @system_id_list (list) - list of system ids for filter
        """

        # create a WorkflowInstanceSet
        if name is None:
            name = self.name + " set"
        if description is None:
            description = f'Set created from {name}'
        new_wfinstanceset = WorkflowInstanceSet.objects.create(name=name, description=description)
        print(f'[DEBUG] created new wfinstanceset name={new_wfinstanceset.name}')

        if filter == "ALL":
            systems = System.objects.all()
        elif filter == "INCLUDE":
            systems = System.objects.filter(id in system_id_list)
        elif filter == "EXCLUDE":
            systems = System.objects.filter(id not in system_id_list)
        else:
            # we have an error
            raise ValueError (f'Unrecongized filter for system in create_system_workflow_instance: {filter}')

        wfinstances = []
        for system in systems:
            wfinstance = self.create_workflowinstance_obj()
            wfinstance.workflowinstanceset = new_wfinstanceset
            wfinstance.name = new_wfinstanceset.name
            wfinstance.system = system
            # tweak instance workflow json
            # set current item
            # add tag(s)
            # update log to indicate created from workflowimage <uuid>
            print(f'[DEBUG] created new wfinstance name={wfinstance.name}')
            wfinstances.append(wfinstance)

        # bulk create wfinstances    
        new_wfinstances = WorkflowInstance.objects.bulk_create(wfinstances)
        print(f'[DEBUG] Created {len(new_wfinstances)} instances')
        return new_wfinstanceset


class WorkflowInstanceSet(auto_prefetch.Model, TagModelMixin, BaseModel):
    name = models.CharField(max_length=100, help_text="Descriptive name", unique=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier")
    workflowimage = auto_prefetch.ForeignKey(WorkflowImage, null=True, related_name="workflowinstancesets", on_delete=models.SET_NULL,
                                            help_text="WorkflowImage")
    description = models.CharField(max_length=250, help_text="Brief description", unique=False, blank=True, null=True)

    def __str__(self):
        return f'<WorkflowInstanceSet name="{self.name}" id={self.id}>'

    def __repr__(self):
        # For debugging.
        return f'<WorkflowInstanceSet name="{self.name}" id={self.id}>'

    @transaction.atomic
    def delete_workflowinstances(self):
        """Delete all workflowinstances associated with a workflowinstanceset"""

        WorkflowInstance.objects.filter(workflowinstanceset=self).delete()
        return None


class WorkflowInstance(auto_prefetch.Model, TagModelMixin, BaseModel):
    name = models.CharField(max_length=100, help_text="Descriptive name", unique=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier")
    workflow = models.JSONField(blank=True, default=dict, help_text="Workflow object")
    rules = models.JSONField(blank=True, default=dict, help_text="Rules object")
    log = models.JSONField(blank=True, default=dict, help_text="Log object")
    workflowimage = auto_prefetch.ForeignKey(WorkflowImage, null=True, related_name="workflowinstances", on_delete=models.SET_NULL,
                                            help_text="WorkflowImage")
    # parent = models.ForeignKey(WorkflowImage, related_name="children", on_delete=models.SET_NULL,
    #                                          help_text="Parent WorkflowInstance")
    workflowinstanceset = auto_prefetch.ForeignKey(WorkflowInstanceSet, related_name='workflowinstances', on_delete=models.SET_NULL, blank=True,
                                      null=True, help_text="System")
    system = auto_prefetch.ForeignKey(System, related_name='workflowinstances', on_delete=models.CASCADE, blank=True,
                                      null=True, help_text="System")

    def __str__(self):
        return f'<WorkflowInstance name="{self.name}" id={self.id}>'

    def __repr__(self):
        # For debugging.
        return f'<WorkflowInstance name="{self.name}" id={self.id}>'
