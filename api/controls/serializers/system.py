from rest_framework.relations import PrimaryKeyRelatedField

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.element import DetailedElementSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from controls.models import System
from siteapp.models import Tag


class SimpleSystemSerializer(ReadOnlySerializer):
    root_element = DetailedElementSerializer()

    class Meta:
        model = System
        fields = ['root_element', 'fisma_id']


class DetailedSystemSerializer(SimpleSystemSerializer):
    root_element = DetailedElementSerializer()

    class Meta:
        model = System
        fields = SimpleSystemSerializer.Meta.fields + ['root_element']


class WriteElementTagsSerializer(WriteOnlySerializer):
    tag_ids = PrimaryKeyRelatedField(source='tags', many=True, queryset=Tag.objects)

    class Meta:
        model = System
        fields = ['tag_ids']
