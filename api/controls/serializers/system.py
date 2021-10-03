from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.element import DetailedElementSerializer
from controls.models import System


class SimpleSystemSerializer(ReadOnlySerializer):
    class Meta:
        model = System
        fields = ['fisma_id']


class DetailedSystemSerializer(SimpleSystemSerializer):
    root_element = DetailedElementSerializer()

    class Meta:
        model = System
        fields = SimpleSystemSerializer.Meta.fields + ['root_element']
