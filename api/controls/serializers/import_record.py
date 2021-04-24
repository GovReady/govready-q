from api.base.serializers.base import BaseSerializer
from controls.models import Element


class ImportRecordSerializer(BaseSerializer):

    class Meta:
        model = Element
        fields = BaseSerializer.Meta.fields + ['name', 'uuid']


