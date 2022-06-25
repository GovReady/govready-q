from rest_framework_recursive.fields import RecursiveField
from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.element import DetailedElementSerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from controls.models import Statement


class SimpleStatementSerializer(ReadOnlySerializer):
    class Meta:
        model = Statement
        fields = ['sid', 'sid_class', 'pid', 'body', 'statement_type', 'remarks', 'status', 'version', 'uuid']


class DetailedStatementSerializer(SimpleStatementSerializer):
    parent = RecursiveField(required=False, allow_null=True)
    prototype = RecursiveField(required=False, allow_null=True)
    producer_element = DetailedElementSerializer()
    consumer_element = DetailedElementSerializer()
    mentioned_elements = DetailedElementSerializer(many=True)
    import_record = SimpleImportRecordSerializer()

    class Meta:
        model = Statement
        fields = SimpleStatementSerializer.Meta.fields + ['parent', 'prototype', 'producer_element', 'consumer_element',
                                                          'mentioned_elements', 'import_record']
