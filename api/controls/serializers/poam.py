from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.statements import DetailedStatementSerializer
from controls.models import Poam


class SimplePoamSerializer(ReadOnlySerializer):
    class Meta:
        model = Poam
        fields = ['poam_id', 'controls', 'weakness_name', 'weakness_detection_source', 'weakness_source_identifier',
                  'remediation_plan', 'scheduled_completion_date', 'milestones','milestone_changes',
                  'risk_rating_original', 'risk_rating_adjusted', 'poam_group']


class DetailedPoamSerializer(SimplePoamSerializer):
    statement = DetailedStatementSerializer()

    class Meta:
        model = Poam
        fields = SimplePoamSerializer.Meta.fields + ['statement']
