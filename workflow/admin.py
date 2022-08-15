from django.contrib import admin
from .models import WorkflowImage, WorkflowInstanceSet, WorkflowInstance, WorkflowRecipe
from simple_history.admin import SimpleHistoryAdmin
from django_json_widget.widgets import JSONEditorWidget
from jsonfield import JSONField
from django.db import models
from guardian.admin import GuardedModelAdmin


# Register your models here.
class WorkflowRecipeAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'uuid')

class WorkflowImageAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'uuid')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 40em; width: 650px; margin-left: 160px;'})},
    }


class WorkflowInstanceSetAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'uuid', 'description')


class WorkflowInstanceAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'uuid', 'system', 'workflowinstanceset')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 40em; width: 650px; margin-left: 160px;'})},
    }


admin.site.register(WorkflowRecipe, WorkflowRecipeAdmin)
admin.site.register(WorkflowImage, WorkflowImageAdmin)
admin.site.register(WorkflowInstanceSet, WorkflowInstanceSetAdmin)
admin.site.register(WorkflowInstance, WorkflowInstanceAdmin)
