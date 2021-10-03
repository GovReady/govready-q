from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Tag


class SimpleTagSerializer(ReadOnlySerializer):
    class Meta:
        model = Tag
        fields = ['label', 'system_created']


class WriteTagSerializer(WriteOnlySerializer):

    def create(self, validated_data):
        validated_data['system_created'] = False
        return super().create(validated_data)

    class Meta:
        model = Tag
        fields = ['label']
