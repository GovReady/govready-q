from rest_framework import serializers
from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.statements import DetailedStatementSerializer
from controls.models import Poam


class SimplePoamSerializer(ReadOnlySerializer):
    statement = serializers.SerializerMethodField('get_statement')

    def get_statement(self, poam):
        smt = {
            'sid': poam.statement.sid,
            'sid_class': poam.statement.sid_class,
            'source': poam.statement.source,
            'pid': poam.statement.pid,
            'body': poam.statement.body,
            'statement_type': poam.statement.statement_type,
            'remarks': poam.statement.remarks,
            'status': poam.statement.status,
            'version': poam.statement.version,
            'created': poam.statement.created,
            'updated': poam.statement.updated,
            # 'parent': poam.statement.parent,
            # 'prototype': poam.statement.prototype,
            # 'producer_element': poam.statement.producer_element,
            # 'consumer_element': poam.statement.consumer_element,
            # 'mentioned_elements': poam.statement.mentioned_elements,
            'uuid': poam.statement.uuid,
            'import_record': poam.statement.import_record,
            # 'change_log': poam.statement.change_log,
            # 'history': poam.statement.history,
        }
        return smt
    class Meta:
        model = Poam
        fields = ['poam_id', 'controls', 'weakness_name', 'weakness_detection_source', 'weakness_source_identifier',
                  'remediation_plan', 'scheduled_completion_date', 'milestones','milestone_changes',
                  'risk_rating_original', 'risk_rating_adjusted', 'poam_group', 'statement']


class DetailedPoamSerializer(SimplePoamSerializer):
    statement = DetailedStatementSerializer()

    class Meta:
        model = Poam
        fields = SimplePoamSerializer.Meta.fields + ['statement']
