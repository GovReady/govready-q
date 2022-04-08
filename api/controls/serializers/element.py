from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from api.siteapp.serializers.appointment import SimpleAppointmentSerializer
from controls.models import Element, ElementRole, ElementControl
from siteapp.models import Appointment, Role, Party, Tag
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
    # parties = serializers.SerializerMethodField()
    parties = serializers.SerializerMethodField('get_list_of_users')

    

    def get_list_of_users(self, element):
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
    class Meta:
        model = Element
        fields = SimpleElementSerializer.Meta.fields + ['roles', 'import_record', 'tags', 'appointments', 'parties']

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