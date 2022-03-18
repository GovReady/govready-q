from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from controls.models import Element, ElementRole, ElementControl
from siteapp.models import Tag
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

    class Meta:
        model = Element
        fields = SimpleElementSerializer.Meta.fields + ['roles', 'import_record', 'tags']

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
