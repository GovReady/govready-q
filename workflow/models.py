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
from siteapp.models import User
from siteapp.model_mixins.tags import TagModelMixin
from controls.utilities import *

import uuid
import tools.diff_match_patch.python3 as dmp_module
from copy import deepcopy
from django.db import transaction
from django.core.validators import RegexValidator
from django.core.validators import validate_email

# Create your models here.
class WorkflowRecipe(auto_prefetch.Model, TagModelMixin, BaseModel):
    name = models.CharField(max_length=100, help_text="Descriptive name", unique=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier")
    description = models.CharField(max_length=250, help_text="Brief description", unique=False, blank=True, null=True)
    recipe = models.TextField(help_text="Workflow instructions", unique=False, blank=True, null=True)
    # workflow = models.JSONField(blank=True, default=dict, help_text="Workflow object")
    # rules = models.JSONField(blank=True, default=list, help_text="Rules list")

    def __str__(self):
        return f'<WorkflowRecipe name="{self.name}" id={self.id}>'

    def __repr__(self):
        # For debugging.
        return f'<WorkflowRecipe name="{self.name}" id={self.id}>'


class WorkflowImage(auto_prefetch.Model, TagModelMixin, BaseModel):
    name = models.CharField(max_length=100, help_text="Descriptive name", unique=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier")
    workflow = models.JSONField(blank=True, default=dict, help_text="Workflow object")
    rules = models.JSONField(blank=True, default=list, help_text="Rules list")
    workflowrecipe = auto_prefetch.ForeignKey(WorkflowRecipe, null=True, related_name="workflowimages", on_delete=models.SET_NULL,
                                            help_text="WorkflowRecipe")

    def __str__(self):
        return f'<WorkflowImage name="{self.name}" id={self.id}>'

    def __repr__(self):
        # For debugging.
        return f'<WorkflowImage name="{self.name}" id={self.id}>'

    def create_workflowinstance_obj(self):
        """Returns a generic workflowinstance unsaved object from workflowimage."""
        wfinstance = WorkflowInstance()
        wfinstance.workflowimage = self
        wfinstance.name = self.name
        wfinstance.workflow = self.workflow
        wfinstance.rules = self.rules
        # add tag
        return wfinstance

    @transaction.atomic
    def create_orphan_worflowinstance(self, name=None):
        """Create a workflowinstance not associated with any model/objects."""

        wfinstance = self.create_workflowinstance_obj()
        wfinstance.name = name
        wfinstance.save()
        print(f'[DEBUG] Created 1 instance')
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

    def create_workflowrecipe_from_image(self):
        """Create a workflowrecipe from a workflow image."""

        # convert workflow to recipe text
        recipe_features = []
        for f_key in self.workflow['feature_order']:
            feature = self.workflow['features'][f_key]
            cmd = feature['cmd']
            text = feature['text']
            # convert props
            props = []
            for p in feature['props']:
                key = list(p.keys())[0]
                prop = f"{key}({p[key]})"
                props.append(prop)
            # build recipe feature
            recipe_feature = f'{cmd}: {text} {" ".join(props)}'
            recipe_features.append(recipe_feature)
        # convert rules to recipe
        # TODO: convert rules to recipe
        # make sure name doesn't already exist
        workflowrecipe = WorkflowRecipe.objects.create(name=self.name)
        workflowrecipe.description = self.workflow.get('description', None)
        workflowrecipe.recipe = "\n".join(recipe_features)
        workflowrecipe.save()


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
    rules = models.JSONField(blank=True, default=list, help_text="Rules list")
    log = models.JSONField(blank=True, default=list, help_text="Log entries")
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

    @property
    def feature_keys(self):
        """Return feature keys"""
        # return list(self.workflow['features'].keys())
        return self.workflow['feature_order']

    def validate_feature_keys(self):
        """Return True if workflow instance feature_order contains all feature keys"""
        return set(self.workflow['feature_order']) == set(self.self.workflow['features'].keys())

    def set_curr_feature(self, curr_feature, who_name='self'):
        """Set current feature"""
        if curr_feature in self.workflow['features'].keys():
            self.workflow['curr_feature'] = curr_feature
            self.log_event('set_feature_key', f'Set curr_feature_key to {self.workflow["curr_feature"]}', who_name)
        else:
            raise KeyError

    @property
    def curr_feature(self):
        """Return current feature"""
        return self.workflow["curr_feature"]

    @property
    def curr_feature_index(self):
        """Return current feature index from list of features"""
        feature_keys = self.workflow['feature_order']
        return feature_keys.index(self.curr_feature)

    def is_final_feature(self, feature):
        """Returns True if feature is final feature in workflowinstance"""
        if self.feature_keys.index(feature) == len(self.feature_keys) - 1:
            return True
        else:
            return False

    def set_workflowinstance_complete(self):
        """Set workflowinstance complete attribute to True"""
        self.workflow['complete'] = True
        self.log_event('set_workflowinstance_completed', f'Workflow set to completed')
        return True

    def set_workflowinstance_not_complete(self):
        """Set workflowinstance complete attribute to False"""
        self.workflow['complete'] = False
        self.log_event('set_workflowinstance_not_completed', f'Workflow set to not completed')
        return False

    def log_event(self, name, description, who='self'):
        """Log event"""
        event = {
            'name': name,
            'description': description,
            'who': who
        }
        self.log.append(event)
        return event

    def set_curr_feature_completed(self, who='self'):
        """Set specfic feature complete"""
        who_name = User.username if (type(who)==User) else 'self'
        self.workflow['features'][self.workflow['curr_feature']]['status'] = 'completed'
        self.workflow['features'][self.workflow['curr_feature']]['complete'] = True
        self.log_event('set_feature_completed', f'Set {self.curr_feature} to completed', who_name)

    def advance(self, who='self'):
        """Shift curr_feature forward by one"""
        who_name = User.username if (type(who)==User) else 'self'
        # TODO: skip hidden features
        # while not self.is_final_feature(self.curr_feature) and self.workflow['curr_feature']['ask'] == 'skip':
        if not self.is_final_feature(self.curr_feature):
            self.set_curr_feature(self.feature_keys[self.curr_feature_index + 1])
        else:
            self.set_workflowinstance_complete()
        result = self.save()
        print(f'[DEBUG] Save result wfinstance {self.name}: {result}')
        