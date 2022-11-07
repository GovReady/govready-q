from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import SystemSettings, Classification, Sitename

class SystemSettingsAdmin(admin.ModelAdmin):
  list_display = ('setting', 'active', 'details')
  fields = ('setting', 'active', 'details')
  formfield_overrides = {
      models.JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 20em; width: 650px; margin-left: 160px;'})},
  }

admin.site.register(SystemSettings, SystemSettingsAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    admin.site.register(Classification)

class SitenameAdmin(admin.ModelAdmin):
    admin.site.register(Sitename)
