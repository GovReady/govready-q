from django.db import models


class CommonControlProvider(models.Model):
    name = models.CharField(max_length=150, help_text="Name of the CommonControlProvider", unique=True)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)

    def __str__(self):
        return self.name

class CommonControl(models.Model):
    name = models.CharField(max_length=150, help_text="Name of the CommonControl", unique=True, blank=True, null=True)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)
    oscal_ctl_id = models.CharField(max_length=20, help_text="OSCAL formatted Control ID (e.g., au-2.3)", blank=True, null=True)
    legacy_imp_smt = models.TextField(help_text="Legacy large implementation statement", unique=False, blank=True, null=True,)
    common_control_provider =  models.ForeignKey(CommonControlProvider, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# class Statement(models.Model):
#     sid = models.CharField(max_length=100, help_text="Unique Statement identifier", unique=True, bank=False, null=False)
#     body = models.TextField(help_text="The statement itself", unique=False, bank=True, null=True)
#     stype = models.CharField(max_length=150, help_text="Statement type", unique=False, bank=True, null=True)
#     parent = models.ForeignKey(Statement, on_delete=models.SET_NULL, bank=True, null=True)
#     created = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated = models.DateTimeField(auto_now_add=True, db_index=True)

    # def __str__(self):
    #     return "<%s/%s(%d)>" % (self.sid, self.id)

    # def __repr__(self):
    #     # For debugging.
    #     return "<%s/%s(%d)>" % (self.sid, self.id)

