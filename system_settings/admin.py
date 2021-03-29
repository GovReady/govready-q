from django.contrib import admin

from .models import SystemSettings, Classification, Sitename

class SystemSettingsAdmin(admin.ModelAdmin):
  list_display = ('setting', 'active')
  fields = ('setting', 'active')

admin.site.register(SystemSettings, SystemSettingsAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    admin.site.register(Classification)

class SitenameAdmin(admin.ModelAdmin):
    admin.site.register(Sitename)
