from rest_framework.relations import PrimaryKeyRelatedField

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from controls.models import Element, ElementRole, ElementControl
from siteapp.models import Tag


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
