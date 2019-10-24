from django import forms
from django.forms import ModelForm

from itsystems.models import SystemInstance
from itsystems.models import HostInstance
from itsystems.models import Agent

class SystemInstanceForm(ModelForm):

    class Meta:
        model = SystemInstance
        fields = ['name', 'sdlc_stage']
        labels = {
            'name': ('Name'),
            'sdlc_stage': ('Software Development Life Cycle (SDLC) Stage'),
        }

class HostInstanceForm(ModelForm):

    class Meta:
        model = HostInstance
        fields = ['name', 'host_type', 'os', 'system_instance']
        labels = {
            'name': ('Name'),
            'host_type': ('Host Type'),
            'os': ('Operating System'),
            'system_instance': ('System Instance'),
        }

class AgentForm(ModelForm):

    class Meta:
        model = Agent
        fields = ['agent_id', 'agent_service', 'host_instance',]
        labels = {
            'agent_id': ('Agent Id'),
            'agent_service': ('Agent Service'),
            'host_instance': ('Host Instance'),
        }