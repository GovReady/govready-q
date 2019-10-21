from django.contrib import admin

from .models import SystemInstance, HostInstance, AgentService, Agent


class HostInstancesInLine(admin.TabularInline):
    model = HostInstance

class AgentInLine(admin.TabularInline):
    model = Agent

class SystemInstanceAdmin(admin.ModelAdmin):
    ordering = ('name', 'sdlc_stage')
    list_display = ('name', 'sdlc_stage', 'id')
    inlines = [
        HostInstancesInLine,
    ]

class HostInstanceAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'system_instance', 'host_type', 'os')
    inlines = [
        AgentInLine,
    ]

class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'host_instance', 'agent_service')

admin.site.register(SystemInstance, SystemInstanceAdmin)
admin.site.register(HostInstance, HostInstanceAdmin)
admin.site.register(AgentService)
admin.site.register(Agent, AgentAdmin)
