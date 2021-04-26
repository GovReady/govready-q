from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.deployment import DetailedDeploymentSerializer
from api.controls.serializers.system import DetailedSystemSerializer
from controls.models import SystemAssessmentResult


class SimpleSystemAssessmentResultSerializer(ReadOnlySerializer):
    class Meta:
        model = SystemAssessmentResult
        fields = ['name', 'description', 'uuid', 'assessment_results']


class DetailedSystemAssessmentResultSerializer(SimpleSystemAssessmentResultSerializer):
    system = DetailedSystemSerializer()
    deployment = DetailedDeploymentSerializer()

    class Meta:
        model = SystemAssessmentResult
        fields = SimpleSystemAssessmentResultSerializer.Meta.fields + ['system', 'deployment']
