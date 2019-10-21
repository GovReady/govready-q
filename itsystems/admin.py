from django.contrib import admin

from .models import SystemInstance, HostInstance, AgentService, Agent


class SystemInstanceAdmin(admin.ModelAdmin):
    ordering = ('name', 'sdlc_stage')
    list_display = ('name', 'sdlc_stage', 'id')

class HostInstanceAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'system_instance', 'host_type', 'os')

admin.site.register(SystemInstance, SystemInstanceAdmin)
admin.site.register(HostInstance, HostInstanceAdmin)
admin.site.register(AgentService)
admin.site.register(Agent)
