from rest_framework import serializers
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

class SystemCreateAndSetProposalSerializer(WriteOnlySerializer):
    userId = serializers.IntegerField(max_value=None, min_value=None)
    elementId = serializers.IntegerField(max_value=None, min_value=None)
    criteria_comment = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    status = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    class Meta:
        model = System
        fields = ['userId', 'elementId', 'criteria_comment','status']


class SystemRetrieveProposalsSerializer(ReadOnlySerializer):
    proposals = serializers.SerializerMethodField('get_proposals')

    def get_proposals(self, system):
        list_of_proposals = []
        counter = 1
        for proposal in system.proposals.all():
            list_of_proposals.append({
                'id': counter,
                'proposal_id': proposal.id,
                'user': proposal.user.username,
                'elementId': proposal.requested_element.id,
                'element_name': proposal.requested_element.name,
                'criteria_comment': proposal.criteria_comment,
                'status': proposal.status,
            })
            counter += 1
        return list_of_proposals
    class Meta:
        model = System
        fields = ['proposals']