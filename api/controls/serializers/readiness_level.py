from api.base.serializers.types import ReadOnlySerializer
from controls.models import Statement


class SimpleReadinessLevelSerializer(ReadOnlySerializer):

    class Meta:
        model = Element
        fields = ['readiness_level']


