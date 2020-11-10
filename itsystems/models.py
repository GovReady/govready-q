from django.db import models, transaction
from django.utils import crypto, timezone
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)


class SystemInstance(models.Model):
    name = models.CharField(max_length=255, help_text="The name of this IT System Instance.", unique=True)
    sdlc_stage = models.CharField(max_length=24, null=True, blank=True, help_text="The stage of the System Development Life Cycle System is in.")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin, notification strings
        return self.name

    def get_absolute_url(self):
        return "/itsystems/%s/" % (self.id)

    def get_hostinstances(self):
        return HostInstance.objects.filter(system_instance__pk=self.pk)

class HostInstance(models.Model):
    name = models.CharField(max_length=255, help_text="The name of this Host Instance (e.g., workload/endpoint/server).", unique=True)
    host_type = models.CharField(max_length=24, null=True, blank=True, help_text="A categorization of the host.")
    os = models.CharField(max_length=155, null=True, blank=True, help_text="The Operating System running on the Host Instance.")
    system_instance = models.ForeignKey(SystemInstance, blank=True, null=True, related_name="hostinstances", on_delete=models.SET_NULL, help_text="The SystemInstance to which this HostInstance belongs.")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin, notification strings
        return self.name

    def get_agents(self):
        return Agent.objects.filter(host_instance__pk=self.pk)

    def get_first_agent(self):
        return Agent.objects.filter(host_instance__pk=self.pk)[0]

class AgentService(models.Model):
    name = models.CharField(max_length=255, help_text="The name of this endpoint/host Agent Service .", unique=True)
    api_user = models.CharField(max_length=255, null=True, blank=True, help_text="The user/login identify for accessing Agent Service's API.")
    api_pw = models.CharField(max_length=255, null=True, blank=True, help_text="The user/login password for accessing Agent Service's API.")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin, notification strings
        return self.name

class Agent(models.Model):
    agent_id = models.CharField(max_length=24, help_text="The unique identifier of an installed Agent on a Host Instance.")
    agent_service = models.ForeignKey(AgentService, null=False, blank=False, related_name="agents", on_delete=models.CASCADE, help_text="The AgentService to which this Agent belonts.")
    host_instance = models.ForeignKey(HostInstance, null=True, blank=True, related_name="agents", on_delete=models.SET_NULL, help_text="The HostInstance on which the Agent is installed and monitoring.")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin, notification strings
        return self.agent_id

class Vendor(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False, help_text="The name of the Vendor.", unique=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin, notification strings
        return self.name

class Component(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False, help_text="The unique name of a usable component.")
    vendor = models.ForeignKey(Vendor, null=False, blank=False, related_name="components", 
        on_delete=models.CASCADE, help_text="The vendor who supports or sells this component.")
    version = models.CharField(max_length=50, null=True, blank=True, help_text="The current version number for this component.")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin, notification strings
        return self.name