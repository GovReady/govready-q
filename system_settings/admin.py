from django.contrib import admin

from .models import SystemSettings

class SystemSettingsAdmin(admin.ModelAdmin):
  list_display = ('setting', 'active')
  fields = ('setting', 'active')

admin.site.register(SystemSettings, SystemSettingsAdmin)
