from api.base.serializers.base import BaseSerializer
from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.import_record import ImportRecordSerializer
from api.siteapp.serializers.tags import TagSerializer
from controls.models import Element, ElementRole


class ElementRoleSerializer(BaseSerializer):
    class Meta:
        model = ElementRole
        fields = ['role', 'description']


class DetailedElementSerializer(ReadOnlySerializer):
    import_record = ImportRecordSerializer(read_only=True)
    roles = ElementRoleSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Element
        fields = ['name', 'full_name', 'description', 'element_type', 'roles', 'uuid', 'import_record', 'tags']


class WriteElementSerializer(WriteOnlySerializer):
    # import_record = ImportRecordSerializer(read_only=True)
    # roles = ElementRoleSerializer(many=True)
    # tags = TagSerializer(many=True)

    class Meta:
        model = Element
        fields = ['name']
