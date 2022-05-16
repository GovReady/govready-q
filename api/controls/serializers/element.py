from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField


from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from api.siteapp.serializers.appointment import SimpleAppointmentSerializer
from controls.models import Element, ElementRole, ElementControl, Statement
from controls.enums.statements import StatementTypeEnum
from siteapp.models import Appointment, Party, Request, Role, Tag
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)

class SimpleElementRoleSerializer(ReadOnlySerializer):
    class Meta:
        model = ElementRole
        fields = ['role', 'description']


class SimpleElementSerializer(ReadOnlySerializer):
    class Meta:
        model = Element
        fields = ['name', 'full_name', 'description', 'element_type', 'uuid']


class DetailedElementSerializer(SimpleElementSerializer):
    import_record = SimpleImportRecordSerializer()
    roles = SimpleElementRoleSerializer(many=True)
    tags = SimpleTagSerializer(many=True)
    appointments = SimpleAppointmentSerializer(many=True)
    parties = serializers.SerializerMethodField('get_parties')
    criteria = serializers.SerializerMethodField('get_criteria')
    numOfStmts = serializers.SerializerMethodField('get_numOfStmts')

    def get_numOfStmts(self, element):
        stmts = Statement.objects.filter(producer_element_id = element.id, statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name)
        return len(stmts)
        
    def get_parties(self, element):
        parties = []
        counter = 1;
        def partyInList(parties_list, party_id):
            for party in parties_list:
                if ('party_id', party_id) in party.items():
                    return True
            return False

        def getParty(parties_list, party_id):
            for party in parties_list:
                if ('party_id', party_id) in party.items():
                    return parties_list.index(party)
            
        for appointment in element.appointments.all():
            if(partyInList(parties, appointment.party.id)):
                par = getParty(parties, appointment.party.id)
                newRole = {
                    "id": appointment.role.id,
                    "appointment_id": appointment.id,
                    "role_id": appointment.role.role_id,
                    "role_title": appointment.role.title,
                    "role_name": appointment.role.short_name,
                }
                parties[par]['roles'].append(newRole)
            else:
                party = {
                    "id": counter,
                    "party_id": appointment.party.id,
                    "uuid":appointment.party.uuid,
                    "party_type":appointment.party.party_type,
                    "name":appointment.party.name,
                    "short_name":appointment.party.short_name,
                    "email":appointment.party.email,
                    "phone_number":appointment.party.phone_number,
                    "roles": [{
                        "id": appointment.role.id,
                        "appointment_id": appointment.id,
                        "role_id": appointment.role.role_id,
                        "role_title": appointment.role.title,
                        "role_name": appointment.role.short_name,
                    }]
                }
                counter += 1
                parties.append(party)
        return parties
    def get_criteria(self, element):
        criteria_results = element.statements_produced.filter(statement_type=StatementTypeEnum.COMPONENT_APPROVAL_CRITERIA.name)
        if len(criteria_results) > 0:
            criteria_text = criteria_results.first().body
        else:
            criteria_text = ""
        return criteria_text
    class Meta:
        model = Element
        fields = SimpleElementSerializer.Meta.fields + ['roles', 'import_record', 'tags', 'appointments', 'parties', 'criteria', 'numOfStmts']

class ElementPermissionSerializer(SimpleElementSerializer):
    users_with_permissions = serializers.SerializerMethodField('get_list_of_users')
    
    def get_list_of_users(self, element):
        users_dict = {} # user_id: permissions
        # Transform get_users_with_perms(element, attach_perms=True) queryset to a dict user id and  perms
        userPermsQS = get_users_with_perms(element, attach_perms=True)
        for user in userPermsQS:
            listOfPerms = list(get_user_perms(user, element))
            users_dict[user.id] = listOfPerms
        return users_dict
    class Meta:
        model = Element
        fields = ['users_with_permissions']

class UpdateElementPermissionSerializer(WriteOnlySerializer):
    users_with_permissions = serializers.JSONField()
    class Meta:
        model = Element
        fields = ['users_with_permissions']
class RemoveUserPermissionFromElementSerializer(WriteOnlySerializer):
    user_to_remove = serializers.JSONField()
    class Meta:
        model = Element
        fields = ['user_to_remove']
class SimpleElementControlSerializer(ReadOnlySerializer):
    class Meta:
        model = ElementControl
        fields = ['oscal_ctl_id', 'oscal_catalog_key', 'smts_updated', 'uuid']

class DetailedElementControlSerializer(SimpleElementControlSerializer):
    element = SimpleImportRecordSerializer()

    class Meta:
        model = ElementControl
        fields = SimpleElementControlSerializer.Meta.fields + ['element']


class WriteElementTagsSerializer(WriteOnlySerializer):
    tag_ids = PrimaryKeyRelatedField(source='tags', many=True, queryset=Tag.objects)

    class Meta:
        model = Element
        fields = ['tag_ids']

class WriteElementAppointPartySerializer(WriteOnlySerializer):
    appointment_ids = PrimaryKeyRelatedField(source='appointment', many=True, queryset=Appointment.objects)
    class Meta:
        model = Element
        fields = ['appointment_ids']

class DeletePartyAppointmentsFromElementSerializer(WriteOnlySerializer):
    party_id_to_remove = serializers.IntegerField(max_value=None, min_value=None)
    class Meta:
        model = Element
        fields = ['party_id_to_remove']

class ElementPartySerializer(ReadOnlySerializer):
    parties = serializers.SerializerMethodField('get_list_of_users')

    def get_list_of_users(self, element):
        list_of_parties = []
        for appointment in element.appointments.all():
            party = {
                "id": appointment.id,
                "party_id": appointment.party.id,
                "uuid":appointment.party.uuid,
                "party_type":appointment.party.party_type,
                "name":appointment.party.name,
                "short_name":appointment.party.short_name,
                "email":appointment.party.email,
                "phone_number":appointment.party.phone_number,
                "role_id": appointment.role.role_id,
                "role_title": appointment.role.title,
                "role_name": appointment.role.short_name,
            }
            list_of_parties.append(party)
        return list_of_parties
    class Meta:
        model = Element
        fields = ['parties']

class CreateMultipleAppointmentsFromRoleIds(WriteOnlySerializer):
    role_ids = serializers.JSONField()
    class Meta:
        model = Element
        fields = ['role_ids']

class ElementRequestsSerializer(ReadOnlySerializer):
    requested = serializers.SerializerMethodField('get_list_of_requested')

    def get_list_of_requested(self, element):
        list_of_requests = []
        counter = 1
        for request in element.requests.all():
            
            list_of_system_PointOfContacts = []
            for user in request.system.root_element.appointments.filter(role__title="Point of Contact"):
                list_of_system_PointOfContacts.append(user.party.name)

            list_of_requestedElements_PointOfContacts = []
            for user in request.requested_element.appointments.filter(role__title="Point of Contact"):
                list_of_requestedElements_PointOfContacts.append(user.party.name)

            req = {
                "id": counter,
                "requestId": request.id,
                "userId": request.user.id,
                "user_name": request.user.name,
                "user_email": request.user.email,
                "user_phone_number": request.user.phone_number,
                "system": {
                    "id": request.system.id,
                    "name": request.system.root_element.name,
                    "full_name": request.system.root_element.full_name,
                    "name": request.system.root_element.name,
                    "description": request.system.root_element.description,
                    "point_of_contact": list_of_system_PointOfContacts,
                },
                "requested_element": {
                    "id": request.requested_element.id,
                    "name": request.requested_element.name,
                    "full_name": request.requested_element.full_name,
                    "name": request.requested_element.name,
                    "description": request.requested_element.description,
                    "private": request.requested_element.private,
                    "require_approval": request.requested_element.require_approval,
                    "point_of_contact": list_of_requestedElements_PointOfContacts,
                },
                "criteria_comment": request.criteria_comment,
                "criteria_reject_comment": request.criteria_reject_comment,
                "status": request.status,
            }
            counter += 1
            list_of_requests.append(req)
        return list_of_requests
    class Meta:
        model = Element
        fields = ['requested']

class ElementSetRequestsSerializer(WriteOnlySerializer):
    requests_ids = PrimaryKeyRelatedField(source='request', many=True, queryset=Request.objects)
    class Meta:
        model = Element
        fields = ['requests_ids']

class ElementCreateAndSetRequestSerializer(WriteOnlySerializer):
    proposalId = serializers.IntegerField(max_value=None, min_value=None)
    userId = serializers.IntegerField(max_value=None, min_value=None)
    systemId = serializers.IntegerField(max_value=None, min_value=None)
    criteria_comment = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    criteria_reject_comment = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    status = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    class Meta:
        model = Element
        fields = ['proposalId', 'userId', 'systemId', 'criteria_comment', 'criteria_reject_comment', 'status']