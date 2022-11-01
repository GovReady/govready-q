from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from controls.models import Prop


class SimplePropSerializer(ReadOnlySerializer):
    class Meta:
        model = Prop
        fields = ['name',  'ns', 'value', 'propsClass', 'remarks']

class WritePropSerializer(WriteOnlySerializer):
    class Meta:
        model = Prop
        fields = ['name',  'ns', 'value', 'propsClass', 'remarks']
