from django.contrib import admin

from .models import SystemSettings, Support

class SystemSettingsAdmin(admin.ModelAdmin):
  list_display = ('setting', 'active')
  fields = ('setting', 'active')

class SupportAdmin(admin.ModelAdmin):
  list_display = ('id', 'support_email',)
  fields = ('support_text', 'support_email', 'support_phone')

admin.site.register(SystemSettings, SystemSettingsAdmin)
admin.site.register(Support, SupportAdmin)
