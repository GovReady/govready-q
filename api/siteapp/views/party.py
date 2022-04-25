from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.party import SimplePartySerializer, WritePartySerializer
from siteapp.models import Party
# from api.siteapp.filters.parties import PartyFilter

class PartyViewSet(ReadWriteViewSet):
    queryset = Party.objects.all()

    serializer_classes = SerializerClasses(retrieve=SimplePartySerializer,
                                           list=SimplePartySerializer,
                                           create=WritePartySerializer,
                                           update=WritePartySerializer,
                                           destroy=WritePartySerializer)
    # filter_class = PartyFilter