from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from django.core import serializers as serial

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.element import DetailedElementSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from controls.models import System, Poam
from siteapp.models import Tag
import json
import types
class SimpleSystemSerializer(ReadOnlySerializer):
    root_element = DetailedElementSerializer()

    class Meta:
        model = System
        fields = ['root_element', 'fisma_id']

class SimpleSystemPoamsSerializer(ReadOnlySerializer):
    data = serializers.SerializerMethodField('system_poams')
    # poams = serial.serialize("json", system.root_element.statements_consumed.filter(statement_type="POAM"))

    def system_poams(self, system):
        list_of_poams = []
        # import ipdb; ipdb.set_trace()

        for poam_statement in system.root_element.statements_consumed.filter(statement_type="POAM"):
            poam = Poam.objects.get(statement=poam_statement)
            poam_instance = {
                "statement": {}
            }
            # Poam
            for key, value in poam.__dict__.items():
                if not isinstance(value, types.FunctionType or types.MethodType) and not key.startswith('_'):
                    print(key, value)
                    poam_instance[key] = value
                    
            # Attach statement Statement
            for key, value in poam_statement.__dict__.items():
                if not isinstance(value, types.FunctionType or types.MethodType) and not key.startswith('_'):
                    poam_instance["statement"][key] = value
            list_of_poams.append(poam_instance)
        return list_of_poams
    class Meta:
        model = System
        fields = ['data']


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