from django.contrib import admin

from .models import SystemInstance, HostInstance, AgentService, Agent


admin.site.register(SystemInstance)
admin.site.register(HostInstance)
admin.site.register(AgentService)
admin.site.register(Agent)
