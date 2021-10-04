from api.base.serializers.types import ReadOnlySerializer
from controls.models import ImportRecord


class SimpleImportRecordSerializer(ReadOnlySerializer):

    class Meta:
        model = ImportRecord
        fields = ['name', 'uuid']


