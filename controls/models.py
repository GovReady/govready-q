from pathlib import Path
import os
import json
from django.db import models
from django.utils.functional import cached_property
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)
from simple_history.models import HistoricalRecords

from .oscal import Catalogs, Catalog
import uuid
import tools.diff_match_patch.python3 as dmp_module
from copy import deepcopy
from django.db import transaction

BASELINE_PATH = os.path.join(os.path.dirname(__file__),'data','baselines')
ORGPARAM_PATH = os.path.join(os.path.dirname(__file__),'data','org_defined_parameters')

class ImportRecord(models.Model):
    name = models.CharField(max_length=100, help_text="File name of the import", unique=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="Unique identifier for this Import Record.")

    def get_components_statements(self):
        components = Element.objects.filter(import_record=self)
        component_statements = {}

        for component in components:
            component_statements[component] = Statement.objects.filter(producer_element=component)

        return component_statements

STATEMENT_SYNCHED = 'synched'
STATEMENT_NOT_SYNCHED = 'not_synched'
STATEMENT_ORPHANED = 'orphaned'

class SystemException(Exception):
    """Class for raising custom exceptions with Systems"""
    pass

class Statement(models.Model):
    sid = models.CharField(max_length=100, help_text="Statement identifier such as OSCAL formatted Control ID", unique=False, blank=True, null=True)
    sid_class = models.CharField(max_length=200, help_text="Statement identifier 'class' such as 'NIST_SP-800-53_rev4' or other OSCAL catalog name Control ID.", unique=False, blank=True, null=True)
    pid = models.CharField(max_length=20, help_text="Statement part identifier such as 'h' or 'h.1' or other part key", unique=False, blank=True, null=True)
    body = models.TextField(help_text="The statement itself", unique=False, blank=True, null=True)
    statement_type = models.CharField(max_length=150, help_text="Statement type.", unique=False, blank=True, null=True)
    remarks = models.TextField(help_text="Remarks about the statement.", unique=False, blank=True, null=True)
    status = models.CharField(max_length=100, help_text="The status of the statement.", unique=False, blank=True, null=True)
    version = models.CharField(max_length=20, help_text="Optional version number.", unique=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    parent = models.ForeignKey('self', help_text="Parent statement", related_name="children", on_delete=models.SET_NULL, blank=True, null=True)
    prototype = models.ForeignKey('self', help_text="Prototype statement", related_name="instances", on_delete=models.SET_NULL, blank=True, null=True)
    producer_element = models.ForeignKey('Element', related_name='statements_produced', on_delete=models.SET_NULL, blank=True, null=True, help_text="The element producing this statement.")
    consumer_element = models.ForeignKey('Element', related_name='statements_consumed', on_delete=models.SET_NULL, blank=True, null=True, help_text="The element the statement is about.")
    mentioned_elements = models.ManyToManyField('Element', related_name='statements_mentioning', blank=True, help_text="All elements mentioned in a statement; elements with a first degree relationship to the statement.")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, help_text="A UUID (a unique identifier) for this Statement.")
    import_record = models.ForeignKey(ImportRecord, related_name="import_record_statements", on_delete=models.CASCADE,
                                      unique=False, blank=True, null=True, help_text="The Import Record which created this Statement.")
    history = HistoricalRecords(cascade_delete_history=True)
    class Meta:
        indexes = [models.Index(fields=['producer_element'], name='producer_element_idx'),]
        permissions = [('can_grant_smt_owner_permission', 'Grant a user statement owner permission'),]
        ordering = ['producer_element__name', 'sid']

    def __str__(self):
        return "'%s %s %s %s %s'" % (self.statement_type, self.sid, self.pid, self.sid_class, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s %s %s %s %s'" % (self.statement_type, self.sid, self.pid, self.sid_class, self.id)

    @cached_property
    def producer_element_name(self):
        return self.producer_element.name

    @property
    def catalog_control(self):
        """Return the control content from the catalog"""
        # Get instance of the control catalog
        catalog = Catalog.GetInstance(catalog_key=self.sid_class)
        # Look up control by ID
        return catalog.get_control_by_id(self.sid)

    @property
    def catalog_control_as_dict(self):
        """Return the control content from the catalog"""
        # Get instance of the control catalog
        catalog = Catalog.GetInstance(catalog_key=self.sid_class)
        catalog_control_dict = catalog.get_flattened_controls_all_as_dict()
        # Look up control by ID
        return catalog_control_dict[self.sid]

    def create_prototype(self):
        """Creates a prototype statement from an existing statement and prototype object"""

        if self.prototype is not None:
            # Prototype already exists for statement
            return self.prototype
            # check if prototype content is the same, report error if not, or overwrite if permission approved
        prototype = deepcopy(self)
        prototype.statement_type="control_implementation_prototype"
        prototype.consumer_element_id = None
        prototype.id = None
        prototype.save()
        # Set prototype attribute on the instances to newly created prototype
        self.prototype = prototype
        self.save()
        return self.prototype

    def create_instance_from_prototype(self, consumer_element_id):
        """Creates a control_implementation statement instance for a system's root_element from an existing control implementation prototype statement"""

        # TODO: Check statement is a prototype

        # System already has instance of the control_implementation statement
        # TODO: write check for this logic
        # Get all statements for consumer element so we can identify
        smts_existing = Statement.objects.filter(consumer_element__id = consumer_element_id, statement_type = "control_implementation")
        print(smts_existing)
        # Get prototype ids for all consumer element statements
        smts_existing_prototype_ids = [smt.prototype.id for smt in smts_existing]
        if self.id is smts_existing_prototype_ids:
            return self.prototype

        #     # TODO:
        #     # check if prototype content is the same, report error if not, or overwrite if permission approved

        instance = deepcopy(self)
        instance.statement_type="control_implementation"
        instance.consumer_element_id = consumer_element_id
        instance.id = None
        # Set prototype attribute to newly created instance
        instance.prototype = self
        instance.save()
        return instance

    @property
    def prototype_synched(self):
        """Returns one of STATEMENT_SYNCHED, STATEMENT_NOT_SYNCHED, STATEMENT_ORPHANED for control_implementations"""

        if self.statement_type == "control_implementation":
            if self.prototype:
                if self.body == self.prototype.body:
                    return STATEMENT_SYNCHED
                else:
                    return STATEMENT_NOT_SYNCHED
            else:
                return STATEMENT_ORPHANED
        else:
            return STATEMENT_NOT_SYNCHED

    @property
    def diff_prototype_main(self):
        """Generate a diff of statement of type `control_implementation` and its prototype"""

        if self.statement_type != 'control_implementation':
            # TODO: Should we return None or raise error because statement is not of type control_implementation?
            return None
        if self.prototype is None:
            # TODO: Should we return None or raise error because statement does not have a prototype?
            return None
        dmp = dmp_module.diff_match_patch()
        diff = dmp.diff_main(self.prototype.body, self.body)
        return diff

    @property
    def diff_prototype_prettyHtml(self):
        """Generate a diff of statement of type `control_implementation` and its prototype"""

        if self.statement_type != 'control_implementation':
            # TODO: Should we return None or raise error because statement is not of type control_implementation?
            return None
        if self.prototype is None:
            # TODO: Should we return None or raise error because statement does not have a prototype?
            return None
        dmp = dmp_module.diff_match_patch()
        diff = dmp.diff_main(self.prototype.body, self.body)
        return dmp.diff_prettyHtml(diff)

    # TODO:c
    #   - On Save be sure to replace any '\r\n' with '\n' added by round-tripping with excel


class Element(models.Model):
    name = models.CharField(max_length=250, help_text="Common name or acronym of the element", unique=True, blank=False, null=False)
    full_name =models.CharField(max_length=250, help_text="Full name of the element", unique=False, blank=True, null=True)
    description = models.CharField(max_length=255, help_text="Brief description of the Element", unique=False, blank=False, null=False)
    element_type = models.CharField(max_length=150, help_text="Component type", unique=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="A UUID (a unique identifier) for this Element.")
    import_record = models.ForeignKey(ImportRecord, related_name="import_record_elements", on_delete=models.CASCADE,
                                      unique=False, blank=True, null=True, help_text="The Import Record which created this Element.")

    # Notes
    # Retrieve Element controls where element is e to answer "What controls selected for a system?" (System is an element.)
    #    element_id = 8
    #    e = Element.objects.get(id=element_id);
    #    e.controls.all()
    #    # returns <QuerySet ['ac-2 id=1', 'ac-3 id=2', 'au-2 id=3']>
    #
    # Retrieve statements
    #    e.statements_consumed.all()
    #
    # Retrieve statements that are control implementations
    #    e.statements_consumed.filter(statement_type="control_implementation")

    def __str__(self):
        return "'%s id=%d'" % (self.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.name, self.id)

    def assign_owner_permissions(self, user):
        try:
            permissions = get_perms_for_model(Element)
            for perm in permissions:
                assign_perm(perm.codename, user, self)
            return True
        except:
            return False

    def assign_edit_permissions(self, user):
        try:
            permissions = ['view_element', 'change_element', 'add_element']
            for perm in permissions:
                assign_perm(perm, user, self)
            return True
        except:
            return False

    def assign_baseline_controls(self, user, baselines_key, baseline_name):
        """Assign set of controls from baseline to an element"""

        # Usage
            # s = System.objects.get(pk=20)
            # s.root_element.assign_baseline_controls('NIST_SP-800-53_rev4', 'low')

        can_assign_controls = user.has_perm('change_element', self)
        # Does user have edit permissions on system?
        if  can_assign_controls:
            from controls.models import Baselines
            bs = Baselines()
            controls = bs.get_baseline_controls(baselines_key, baseline_name)
            for oscal_ctl_id in controls:
                ec = ElementControl(element=self, oscal_ctl_id=oscal_ctl_id, oscal_catalog_key=baselines_key)
                ec.save()
            return True
        else:
            # print("User does not have permission to assign selected controls to element's system.")
            return False

    def statements(self, statement_type):
        """Return on the statements of statement_type produced by this element"""
        smts = Statement.objects.filter(producer_element = self, statement_type = statement_type)
        return smts

    @transaction.atomic
    def copy(self, name=None):
        """Return a copy of an existing system element as a new element with duplicate control_implementation_prototype statements"""

        # Copy only elements that are components. Do not copy an element of type "system"
        # Components that are systems should always be associated with a project (at least currently).
        # Also, statement structure for a system would be very different.
        if self.element_type == "system":
            raise SystemException("Copying an entire system is not permitted.")

        e_copy = deepcopy(self)
        e_copy.id = None
        if name is not None:
            e_copy.name = name
        else:
            e_copy.name = self.name + " copy"
        e_copy.save()
        # Copy prototype statements from existing element
        for smt in self.statements("control_implementation_prototype"):
            smt_copy = deepcopy(smt)
            smt_copy.producer_element = e_copy
            smt_copy.consumer_element_id = None
            smt_copy.id = None
            smt_copy.save()
        return e_copy

    @property
    def selected_controls_oscal_ctl_ids(self):
        """Return array of selectecd controls oscal ids"""
        # oscal_ids = self.controls.all()
        oscal_ctl_ids = [control.oscal_ctl_id for control in self.controls.all()]
        return oscal_ctl_ids

class ElementControl(models.Model):
    element = models.ForeignKey(Element, related_name="controls", on_delete=models.CASCADE, help_text="The Element (e.g., System, Component, Host) to which controls are associated.")
    oscal_ctl_id = models.CharField(max_length=20, help_text="OSCAL formatted Control ID (e.g., au-2.3)", blank=True, null=True)
    oscal_catalog_key = models.CharField(max_length=100, help_text="Catalog key from which catalog file can be derived (e.g., 'NIST_SP-800-53_rev4')", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    smts_updated = models.DateTimeField(auto_now=False, db_index=True, help_text="Store date of most recent statement update", blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, help_text="A UUID (a unique identifier) for this ElementControl.")

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
            selected_controls[cl['oscal_ctl_id']] = {'oscal_ctl_id': cl['oscal_ctl_id'],
                                                     'oscal_catalog_key': cl['oscal_catalog_key'],
                                                     'uuid': cl['uuid']
                                                     }
        return selected_controls

    def get_flattened_oscal_control_as_dict(self):
        cg = Catalog.GetInstance(catalog_key=self.oscal_catalog_key)
        return cg.get_flattened_control_as_dict(cg.get_control_by_id(self.oscal_ctl_id))

    # def get_flattened_impl_smt_as_dict(self):
    #     """Return the implementation statement for this ElementControl combination"""
    #     # For development let's hardcode what we return
    #     impl_smt = {"sid": "impl_smt sid", "body": "This is the statement itself"}
    #     # Error checking
    #     return impl_smt

class System(models.Model):
    root_element = models.ForeignKey(Element, related_name="system", on_delete=models.CASCADE, help_text="The Element that is this System. Element must be type [Application, General Support System]")
    fisma_id = models.CharField(max_length=40, help_text="The FISMA Id of the system", unique=False, blank=True, null=True)

    # Notes
    # Retrieve system implementation statements
    #   system = System.objects.get(pk=2)
    #   system.root_element.statements_consumed.filter(statement_type="control_implementation")
    #
    # Retrieve system common controls statements
    #   system = System.objects.get(pk=2)
    #   system.root_element.common_controls.all()[0].common_control.legacy_imp_smt
    #   system.root_element.common_controls.all()[0].common_control.body
    #

    def __str__(self):
        return "'System %s id=%d'" % (self.root_element.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'System %s id=%d'" % (self.root_element.name, self.id)

    # @property
    # def statements_consumed(self):
    #     smts = self.root_element.statements_consumed.all()
    #     return smts

    def assign_owner_permissions(self, user):
        try:
            permissions = get_perms_for_model(System)
            for perm in permissions:
                assign_perm(perm.codename, user, self)
            return True
        except:
            return False

    def assign_edit_permissions(self, user):
        try:
            permissions = ['view_system', 'change_system', 'add_system']
            for perm in permissions:
                assign_perm(perm, user, self)
            return True
        except:
            return False

    @property
    def smts_common_controls_as_dict(self):
        common_controls = self.root_element.common_controls.all()
        smts_as_dict = {}
        for cc in common_controls:
            if cc.common_control.oscal_ctl_id in smts_as_dict:
                smts_as_dict[cc.common_control.oscal_ctl_id].append(cc)
            else:
                smts_as_dict[cc.common_control.oscal_ctl_id] = [cc]
        return smts_as_dict

    @property
    def smts_control_implementation_as_dict(self):
        smts = self.root_element.statements_consumed.filter(statement_type="control_implementation").order_by('pid')
        smts_as_dict = {}
        for smt in smts:
            if smt.sid in smts_as_dict:
                smts_as_dict[smt.sid]['control_impl_smts'].append(smt)
            else:
                smts_as_dict[smt.sid] = {"control_impl_smts": [smt], "common_controls": [], "combined_smt": ""}
        return smts_as_dict

    @cached_property
    def control_implementation_as_dict(self):
        pid_current = None

        # Fetch all selected controls
        elm = self.root_element
        selected_controls = elm.controls.all().values("oscal_ctl_id", "uuid")
        # Get the smts_control_implementations ordered by part, e.g. pid
        smts = elm.statements_consumed.filter(statement_type="control_implementation").order_by('pid')

        smts_as_dict = {}

        # Retrieve all of the existing statements
        for smt in smts:
            if smt.sid in smts_as_dict:
                smts_as_dict[smt.sid]['control_impl_smts'].append(smt)
            else:

                try:
                    elementcontrol = self.root_element.controls.get(oscal_ctl_id=smt.sid, oscal_catalog_key=smt.sid_class)
                    smts_as_dict[smt.sid] = {"control_impl_smts": [smt],
                                         "common_controls": [],
                                         "combined_smt": "",
                                         "elementcontrol_uuid": elementcontrol.uuid,
                                         "combined_smt_uuid": uuid.uuid4()
                                         }
                except ElementControl.DoesNotExist:
                    # Handle case where Element control does not exist
                    elementcontrol = None
                    smts_as_dict[smt.sid] = {"control_impl_smts": [smt],
                                             "common_controls": [],
                                             "combined_smt": "",
                                             "elementcontrol_uuid": None,
                                             "combined_smt_uuid": uuid.uuid4()
                                             }

            # Build combined statement

            # Define status options
            impl_statuses = ["Not implemented", "Planned", "Partially implemented", "Implemented", "Unknown"]
            status_str = ""
            for status in impl_statuses:
                if (smt.status is not None) and (smt.status.lower() == status.lower()):
                    status_str += f'[x] {status} '
                else:
                    status_str += f'<span style="color: #888;">[ ] {status}</span> '
            # Conditionally add statement part in the beginning of a block of statements related to a part
            if smt.pid != "" and smt.pid != pid_current:
                smts_as_dict[smt.sid]['combined_smt'] += f"{smt.pid}.\n"
                pid_current = smt.pid
            # DEBUG
            # TODO
            # Poor performance, at least in some instances, appears to being caused by `smt.prouder_element.name`
            # parameter in the below statement.
            smts_as_dict[smt.sid]['combined_smt'] += f"<i>{smt.producer_element.name}</i>\n{status_str}\n\n{smt.body}\n\n"
            # When "smt.producer_element.name" the provided as a fixed string (e.g, "smt.producer_element.name")
            # for testing purposes, the loop runs 3x faster
            # The reference `smt.prouder_element.name` appears to be calling the database and creating poor performance
            # even where there are no statements.

        # Deprecated implementation of inherited/common controls
        # Leave commented out until we can fully delete...Greg - 2020-10-12
        # # Add in the common controls
        # for cc in self.root_element.common_controls.all():
        #     if cc.common_control.oscal_ctl_id in smts_as_dict:
        #         smts_as_dict[smt.sid]['common_controls'].append(cc)
        #     else:
        #         smts_as_dict[cc.common_control.oscal_ctl_id] = {"control_impl_smts": [], "common_controls": [cc], "combined_smt": ""}
        #     # Build combined statement
        #     smts_as_dict[cc.common_control.oscal_ctl_id]['combined_smt'] += "{}\n{}\n\n".format(cc.common_control.name, cc.common_control.body)

        # Populate any controls from assigned baseline that do not have statements
        for ec in selected_controls:
            if ec.get('oscal_ctl_id') not in smts_as_dict:
                smts_as_dict[ec.get('oscal_ctl_id')] = {"control_impl_smts": [],
                                         "common_controls": [],
                                         "combined_smt": "",
                                         "elementcontrol_uuid": ec.get('ec.uuid'),
                                         "combined_smt_uuid": uuid.uuid4()
                                         }

        # Return the dictionary
        return smts_as_dict

    # @property (See below for creation of property from method)
    def get_producer_elements(self):
        smts = self.root_element.statements_consumed.all()
        components = set()
        for smt in smts:
            if smt.producer_element:
                components.add(smt.producer_element)
        components = list(components)
        components.sort(key = lambda component:component.name)
        return components

    producer_elements = property(get_producer_elements)

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

class ElementCommonControl(models.Model):
    element = models.ForeignKey(Element, related_name="common_controls", on_delete=models.CASCADE, help_text="The Element (e.g., System, Component, Host) to which common controls are associated.")
    common_control = models.ForeignKey(CommonControl, related_name="element_common_control", on_delete=models.CASCADE, help_text="The Common Control for this association.")
    oscal_ctl_id = models.CharField(max_length=20, help_text="OSCAL formatted Control ID (e.g., au-2.3)", blank=True, null=True)
    oscal_catalog_key = models.CharField(max_length=100, help_text="Catalog key from which catalog file can be derived (e.g., 'NIST_SP-800-53_rev4')", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [('element', 'common_control', 'oscal_ctl_id', 'oscal_catalog_key')]

    def __str__(self):
        return f"'{self.element} {self.common_control} {self.oscal_ctl_id} id={self.id}'"

    def __repr__(self):
        # For debugging.
        return f"'{self.element} {self.common_control} {self.oscal_ctl_id} id={self.id}'"

class Baselines (object):
    """Represent list of baselines"""
    def __init__(self):
        global BASELINE_PATH
        self.file_path = BASELINE_PATH
        self.baselines_keys = self._list_keys()
        # self.index = self._build_index()

        # Usage
            # from controls.models import Baselines
            # bs = Baselines()
            # bs.baselines_keys
            # bs53 = bs._load_json('NIST_SP-800-53_rev4')
            # bs53['moderate']['controls']
            # # Returns ['ac-1', 'ac-2', 'ac-2.1', 'ac-2.2', ...]
            # bs.get_baseline_controls('NIST_SP-800-53_rev4', 'moderate')

    def _list_files(self):
        return [
            'NIST_SP-800-53_rev4_baselines.json',
            # 'NIST_SP-800-53_rev5_baselines.json',
            'NIST_SP-800-171_rev1_baselines.json'
        ]

    def _list_keys(self):
        return [
            'NIST_SP-800-53_rev4',
            # 'NIST_SP-800-53_rev5',
            'NIST_SP-800-171_rev1'
        ]

    def _load_json(self, baselines_key):
        """Read baseline file - JSON"""
        # TODO Escape baselines_key
        self.data_file = baselines_key + "_baselines.json"
        data_file = os.path.join(self.file_path, self.data_file)
        # Does file exist?
        if not os.path.isfile(data_file):
            print("ERROR: {} does not exist".format(data_file))
            return False
        # Load file as json
        try:
            with open(data_file, 'r') as json_file:
                data = json.load(json_file)
            return data
        except:
            print("ERROR: {} could not be read or could not be read as json".format(data_file))
            return False

    def get_baseline_controls(self, baselines_key, baseline_name):
        """Return baseline's control OSCAL control ids given baselines key and baseline name"""
        if baselines_key in self.baselines_keys:
            data = self._load_json(baselines_key)
        else:
            print("Requested baselines_key not found in baselines_key data file")
            return False
        if baseline_name in data.keys():
            return data[baseline_name]['controls']
        else:
            print("Requested baseline name not found in baselines_key data file")
            return False

    @property
    def body(self):
        return self.legacy_imp_smt

class OrgParams(object):
    """
    Represent list of organizational defined parameters. Temporary
    class to work with default org params.
    """
    
    _singleton = None
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(OrgParams, cls).__new__(cls)
            cls._singleton.init()
            
        return cls._singleton
    
    def init(self):
        global ORGPARAM_PATH
        self.cache = {}

        path = Path(ORGPARAM_PATH)
        for f in path.glob("*.json"):
            name, values = self.load_param_file(f)
            if name in self.cache:
                raise Exception("Duplicate default organizational parameters name {} from {}".format(name, f))
            self.cache[name] = values
    
    def load_param_file(self, path):
        with path.open("r") as json_file:
            data = json.load(json_file)
            if 'name' in data and 'values' in data:
                return (data["name"], data["values"])
            else:
                raise Exception("Invalid organizational parameters file {}".format(path))
                
    def get_names(self):
        return self.cache.keys()
    
    def get_params(self, name):
        return self.cache.get(name, {})

class Poam(models.Model):
    statement = models.OneToOneField(Statement, related_name="poam", unique=False, blank=True, null=True, on_delete=models.CASCADE, help_text="The Poam details for this statement. Statement must be type Poam.")
    poam_id = models.IntegerField(unique=False, blank=True, null=True, help_text="The sequential ID for the information system.")
    controls = models.CharField(max_length=254, unique=False, blank=True, null=True, help_text="Comma delimited list of security controls affected by the weakness identified.")
    weakness_name = models.CharField(max_length=254, unique=False, blank=True, null=True, help_text="Name for the identified weakness that provides a general idea of the weakness.")
    # weakness_description is found in the Statement.body
    weakness_detection_source = models.CharField(max_length=180, unique=False, blank=True, null=True, help_text=" Name of organization, vulnerability scanner, or other entity that first identified the weakness.")
    weakness_source_identifier = models.CharField(max_length=180, unique=False, blank=True, null=True, help_text="ID or reference provided by the detection source identifying the weakness.")
    # asset_identifier is the Statement.producer_element
    remediation_plan = models.TextField(unique=False, blank=True, null=True, help_text="A high-level summary of the actions required to remediate the plan.")
    scheduled_completion_date = models.DateTimeField(db_index=True, unique=False, blank=True, null=True, help_text="Planned completion date of all milestones.")
    milestones = models.TextField(unique=False, blank=True, null=True, help_text="One or more milestones that identify specific actions to correct the weakness with an associated completion date.")
    milestone_changes = models.TextField(unique=False, blank=True, null=True, help_text="List of changes to milestones.")
    # vendor_dependency = models.CharField(max_length=254, unique=False, blank=True, null=True, help_text="Comma.")
    risk_rating_original = models.CharField(max_length=50, unique=False, blank=True, null=True, help_text="The initial risk rating of the weakness.")
    risk_rating_adjusted = models.CharField(max_length=50, unique=False, blank=True, null=True, help_text="The current or modified risk rating of the weakness.")
    poam_group = models.CharField(max_length=50, unique=False, blank=True, null=True, help_text="A name to collect related POA&Ms together.")
    # spec = JSONField(help_text="A load_modules ModuleRepository spec.", load_kwargs={'object_pairs_hook': OrderedDict})
    # Spec will hold additional values, such as: POC, resources_required, vendor_dependency


    def __str__(self):
        return "<Poam %s id=%d>" % (self.statement, self.id)

    def __repr__(self):
        # For debugging.
        return "<Poam %s id=%d>" % (self.statement, self.id)

    def get_next_poam_id(self, system):
        """Count total number of POAMS and return next linear id"""
        return Statement.objects.filter(statement_type="POAM", consumer_element=system.root_element).count()

    # TODO:
    #   - On Save be sure to replace any '\r\n' with '\n' added by round-tripping with excel
