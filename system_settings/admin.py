from django.contrib import admin

from .models import SystemSettings, Classification, Sitename

class SystemSettingsAdmin(admin.ModelAdmin):
  list_display = ('setting', 'active', 'value', 'value_type', 'description')
  fields = ('setting', 'active', 'value', 'value_type', 'description')


admin.site.register(SystemSettings, SystemSettingsAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    admin.site.register(Classification)

class SitenameAdmin(admin.ModelAdmin):
    admin.site.register(Sitename)
