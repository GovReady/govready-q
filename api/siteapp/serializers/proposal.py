from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Proposal


class SimpleProposalSerializer(ReadOnlySerializer):
    class Meta:
        model = Proposal
        fields = ['user',  'requested_element', 'criteria_comment', 'status']

class WriteProposalSerializer(WriteOnlySerializer):
    class Meta:
        model = Proposal
        fields = ['user', 'requested_element', 'criteria_comment', 'status']
