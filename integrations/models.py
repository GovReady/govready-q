from django.db import models
from django.db.models import Count
from django.utils.functional import cached_property
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)
from simple_history.models import HistoricalRecords
from jsonfield import JSONField
from natsort import natsorted
import uuid
import auto_prefetch
from django.db import transaction

from api.base.models import BaseModel


class Integration(BaseModel):
    name = models.CharField(max_length=250, help_text="Endpoint name in lowercase", unique=False, blank=False, null=False)
    description = models.TextField(default="", help_text="Brief description of the Integration", unique=False, blank=True, null=True)
    config = JSONField(blank=True, null=True, default=dict, help_text="Integration configuration")
    config_schema = JSONField(blank=True, null=True, default=dict, help_text="Integration schema")

    def __str__(self):
        return f"'{self.name} id={self.id}'"

    def __repr__(self):
        return f"'{self.name} id={self.id}'"

    # {
    #     "integrations": [
    #         "csam": {
    #             "authenticate": {
    #                 "personal_access_token": "fsdfkjlkjsdfljk"
    #             }
    #             "map_endpoints": {
    #                 "system_info": "/system/id/{id}"
    #             },
    #             "data": {
    #                 "system_info": {
    #                     "name": "My IT System",
    #                     "system_id": 111
    #                 }
    #             }
    #             "map_data": [
    #                 {
    #                     "local_value": "System.name",
    #                     "integration_value": "system_info['name']"
    #                 }
    #             ]

    #         }
    #     ]
    # }

class Endpoint(auto_prefetch.Model, BaseModel):
    integration = auto_prefetch.ForeignKey(Integration, related_name="endpoints", on_delete=models.CASCADE,
                                            help_text="Endpoint's Integration")
    endpoint_path = models.CharField(max_length=250, help_text="Path to the Endpoint", unique=False, blank=True, null=True)
    description = models.TextField(default="", help_text="Brief description of the endpoint", unique=False, blank=True, null=True)
    element_type = models.CharField(max_length=150, help_text="Component type", unique=False, blank=True, null=True)
    data = JSONField(blank=True, null=True, default=dict, help_text="JSON object representing the API results.")
    history = HistoricalRecords(cascade_delete_history=True)

    def __str__(self):
        return f"'{self.integration.name} {self.endpoint_path} id={self.id}'"

    def __repr__(self):
        return f"'{self.integration.name}{self.endpoint_path} id={self.id}'"

    # def get_absolute_url(self):
    #     return f"/integrations/{integration}/data/endpoint{endpoint_path}"
