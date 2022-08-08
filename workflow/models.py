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


class WorkflowInstance(auto_prefetch.Model, TagModelMixin, BaseModel):
    name = models.CharField(max_length=100, help_text="Descriptive name", unique=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier")
    workflow = models.JSONField(blank=True, default=dict, help_text="Workflow object")
    rules = models.JSONField(blank=True, default=dict, help_text="Rules object")
    log = models.JSONField(blank=True, default=dict, help_text="Log object")
    workflowimage = auto_prefetch.ForeignKey(WorkflowImage, null=True, related_name="workflowimage", on_delete=models.SET_NULL,
                                            help_text="WorkflowImage")
    # parent = models.ForeignKey(WorkflowImage, related_name="children", on_delete=models.SET_NULL,
    #                                          help_text="Parent WorkflowInstance")
    system = auto_prefetch.ForeignKey(System, related_name='workflowinstances', on_delete=models.CASCADE, blank=True,
                                      null=True, help_text="System")
