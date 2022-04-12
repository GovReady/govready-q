from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Request


class SimpleRequestSerializer(ReadOnlySerializer):
    class Meta:
        model = Request
        fields = ['user', 'system', 'element', 'req_comment', 'req_reject_comment', 'status', 'created']

class WriteRequestSerializer(WriteOnlySerializer):
    class Meta:
        model = Request
        fields = ['user', 'system', 'element', 'req_comment', 'req_reject_comment', 'status']
