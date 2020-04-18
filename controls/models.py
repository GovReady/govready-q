from django.db import models


class CommonControlProvider(models.Model):
    name = models.CharField(max_length=150, help_text="Name of the CommonControlProvider", unique=True)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)

class CommonControl(models.Model):
    name = models.CharField(max_length=150, help_text="Name of the CommonControl", unique=True, blank=True, null=True)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)
    oscal_ctl_id = models.CharField(max_length=20, help_text="OSCAL formatted Control ID (e.g., au-2.3)", blank=True, null=True)
    legacy_imp_smt = models.TextField(help_text="Legacy large implementation statement", unique=False, blank=True, null=True,)
    common_control_provider =  models.ForeignKey(CommonControlProvider, on_delete=models.CASCADE)
