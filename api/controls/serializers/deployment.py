from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.system import DetailedSystemSerializer
from controls.models import Deployment


class SimpleDeploymentSerializer(ReadOnlySerializer):
    class Meta:
        model = Deployment
        fields = ['name', 'description', 'uuid', 'inventory_items']


class DetailedDeploymentSerializer(SimpleDeploymentSerializer):
    system = DetailedSystemSerializer()

    class Meta:
        model = Deployment
        fields = SimpleDeploymentSerializer.Meta.fields + ['system']
