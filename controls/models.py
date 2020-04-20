from django.db import models


class Statement(models.Model):
    sid = models.CharField(max_length=100, help_text="Statement identifier such as OSCAL formatted Control ID", unique=False, blank=False, null=False)
    sid_class = models.CharField(max_length=200, help_text="Statement identifier 'class' such as '800-53rev4' or other OSCAL catalog name Control ID ", unique=False, blank=False, null=False)
    body = models.TextField(help_text="The statement itself", unique=False, blank=True, null=True)
    statement_type = models.CharField(max_length=150, help_text="Statement type", unique=False, blank=True, null=True)
    remarks = models.TextField(help_text="The statement itself", unique=False, blank=True, null=True)
    version = models.CharField(max_length=20, help_text="Optional version number", unique=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now_add=True, db_index=True)

    parent = models.ForeignKey('self', help_text="Optional version number", on_delete=models.SET_NULL, blank=True, null=True)
    elements = models.ManyToManyField('Element', related_name='statements', blank=True, null=True)

    def __str__(self):
        return "'%s %s %s id=%d'" % (self.sid, self.sid_class, self.statement_type, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s %s %s id=%d'" % (self.sid, self.sid_class, self.statement_type, self.id)

class Element(models.Model):
    name = models.CharField(max_length=250, help_text="Common name or acronym of the element", unique=False, blank=False, null=False)
    full_name =models.CharField(max_length=250, help_text="Full name of the element", unique=False, blank=True, null=True)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)
    element_type = models.CharField(max_length=150, help_text="Statement type", unique=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "'%s id=%d'" % (self.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.name, self.id)

class CommonControlProvider(models.Model):
    name = models.CharField(max_length=150, help_text="Name of the CommonControlProvider", unique=False)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)

    def __str__(self):
        return self.name

class CommonControl(models.Model):
    name = models.CharField(max_length=150, help_text="Name of the CommonControl", unique=False, blank=True, null=True)
    description = models.CharField(max_length=255, help_text="Brief description of the CommonControlProvider", unique=False)
    oscal_ctl_id = models.CharField(max_length=20, help_text="OSCAL formatted Control ID (e.g., au-2.3)", blank=True, null=True)
    legacy_imp_smt = models.TextField(help_text="Legacy large implementation statement", unique=False, blank=True, null=True,)
    common_control_provider =  models.ForeignKey(CommonControlProvider, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

