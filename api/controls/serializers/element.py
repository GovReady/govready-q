from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from api.siteapp.serializers.tags import TagSerializer
from controls.models import Element, ElementRole, ElementControl


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
    tags = TagSerializer(many=True)

    class Meta:
        model = Element
        fields = SimpleElementSerializer.Meta.fields + ['roles', 'import_record', 'tags']


class WriteElementSerializer(WriteOnlySerializer):
    # import_record = SimpleImportRecordSerializer()
    # roles = SimpleElementRoleSerializer(many=True)
    # tags = TagSerializer(many=True)

    class Meta:
        model = Element
        fields = ['name']


class SimpleElementControlSerializer(ReadOnlySerializer):
    class Meta:
        model = ElementControl
        fields = ['oscal_ctl_id', 'oscal_catalog_key', 'smts_updated', 'uuid']


class DetailedElementControlSerializer(SimpleElementControlSerializer):
    element = SimpleImportRecordSerializer()

    class Meta:
        model = ElementControl
        fields = SimpleElementControlSerializer.Meta.fields + ['element']

