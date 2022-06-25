from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.proposal import SimpleProposalSerializer, WriteProposalSerializer
from siteapp.models import Proposal
# from api.siteapp.filters.proposal import ProposalFilter

class ProposalViewSet(ReadWriteViewSet):
    queryset = Proposal.objects.all()

    serializer_classes = SerializerClasses(retrieve=SimpleProposalSerializer,
                                           list=SimpleProposalSerializer,
                                           create=WriteProposalSerializer,
                                           update=WriteProposalSerializer,
                                           destroy=WriteProposalSerializer,
                                           )
    # filter_class = ProposalFilter

