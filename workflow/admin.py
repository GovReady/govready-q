from django.contrib import admin
from .models import WorkflowImage, WorkflowInstance
from simple_history.admin import SimpleHistoryAdmin
from django_json_widget.widgets import JSONEditorWidget
from jsonfield import JSONField
from django.db import models
from guardian.admin import GuardedModelAdmin


# Register your models here.
class WorkflowImageAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'uuid')
    # actions = ["export_as_csv"]
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 40em; width: 650px; margin-left: 160px;'})},
    }


class WorkflowInstanceAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'uuid', 'system')
    # actions = ["export_as_csv"]
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 40em; width: 650px; margin-left: 160px;'})},
    }

admin.site.register(WorkflowImage, WorkflowImageAdmin)
admin.site.register(WorkflowInstance, WorkflowInstanceAdmin)
