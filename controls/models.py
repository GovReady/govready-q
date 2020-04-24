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
    referenced_elements = models.ManyToManyField('Element', related_name='statement_referencing', blank=True)
    described_element = models.ForeignKey('Element', related_name='statement_describing', on_delete=models.SET_NULL, blank=True, null=True)

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

    # Notes
    # Retrieve Element controls where element is e to answer "What controls selected for a system?" (System is an element.)
    #    element_id = 8
    #    e = Element.objects.get(id=element_id);
    #    e.controls.all()
    #    # returns <QuerySet ['ac-2 id=1', 'ac-3 id=2', 'au-2 id=3']>
    #

    def __str__(self):
        return "'%s id=%d'" % (self.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.name, self.id)

class ElementControl(models.Model):
    element = models.ForeignKey(Element, related_name="controls", on_delete=models.CASCADE, help_text="The Element (e.g., System, Component, Host) to which controls are associated.")
    oscal_ctl_id = models.CharField(max_length=20, help_text="OSCAL formatted Control ID (e.g., au-2.3)", blank=True, null=True)
    oscal_catalog_key = models.CharField(max_length=100, help_text="Catalog key from which catalog file can be derived (e.g., 'NIST_SP-800-53_rev4')", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    # Notes
    # from controls.oscal import *;from controls.models import *;
    #     e = Element.objects.get(id=8);
    #     e.name;
    #     ecq = ElementControl.objects.filter(element=e);
    #     ec = ecq[0]
    #     ec.oscal_catalog_key
    #     cg = Catalog(ec.oscal_catalog_key)
    #     print(cg.get_flattened_control_as_dict(cg.get_control_by_id(ec.oscal_ctl_id)))
    #
    #     # Get the flattened oscal control information
    #     ec.get_flattened_oscal_control_as_dict()
    #     # Get Implementation statement if it exists
    #     ec.get_flattened_impl_smt_as_dict()
    #
    #     # Get an element/system by it's element id
    #     e = Element.objects.get(id=8);
    #     e.name;
    #     # Get all ElementControls for the Element
    #     ec_list = ElementControl.objects.filter(element=e);
    #     for ec in ec_list:
    #       print("OSCAL CONTROL")
    #       print(ec.get_flattened_oscal_control_as_dict())
    #       print("Implementation Statement")
    #       print(ec.get_flattened_impl_smt_as_dict())

    class Meta:
        unique_together = [('element', 'oscal_ctl_id', 'oscal_catalog_key')]

    def __str__(self):
        return "'%s id=%d'" % (self.oscal_ctl_id, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.oscal_ctl_id, self.id)

    def get_controls_by_element(self, element):
        query_set = self.objects.filter(element=element)
        selected_controls = {}
        for cl in query_set:
            selected_controls[cl['oscal_ctl_id']] = {'oscal_ctl_id': cl['oscal_ctl_id'], 'oscal_catalog_key': cl['oscal_catalog_key']}
        return selected_controls

    def get_flattened_oscal_control_as_dict(self):
        from .oscal import Catalogs, Catalog
        cg = Catalog.GetInstance(catalog_key=self.oscal_catalog_key)
        return cg.get_flattened_control_as_dict(cg.get_control_by_id(self.oscal_ctl_id))

    def get_flattened_impl_smt_as_dict(self):
        """Return the implementation statement for this ElementControl combination"""
        # For development let's hardcode what we return
        impl_smt = {"sid": "impl_smt sid", "body": "This is the statement itself"}
        # Error checking
        return impl_smt

class System(models.Model):
    root_element = models.ForeignKey(Element, related_name="system", on_delete=models.CASCADE, help_text="The Element that is this System. Element must be type [Application, General Support System]")
    fisma_id = models.CharField(max_length=40, help_text="The FISMA Id of the system", unique=False, blank=True, null=True)

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

