import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Integration, Endpoint
from guardian.admin import GuardedModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from django_json_widget.widgets import JSONEditorWidget
from jsonfield import JSONField
from django.db import models
from controls.admin import ExportCsvMixin


class IntegrationAdmin(SimpleHistoryAdmin, ExportCsvMixin):
    list_display = ('name',)
    search_fields = ('id', 'name')
    actions = ["export_as_csv"]
    readonly_fields = ('created', 'updated')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

class EndpointAdmin(SimpleHistoryAdmin, ExportCsvMixin):
    list_display = ('endpoint_path', 'get_integration_name', 'updated')

    @admin.display(ordering='integration__name', description='Name')
    def get_integration_name(self, obj):
        return obj.integration.name
    search_fields = ('id', 'endpoint_path')
    actions = ["export_as_csv"]
    readonly_fields = ('created', 'updated')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

admin.site.register(Integration, IntegrationAdmin)
admin.site.register(Endpoint, EndpointAdmin)
