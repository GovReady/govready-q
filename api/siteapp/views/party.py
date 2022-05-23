from django.db.models import Q
from rest_framework import filters

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.party import SimplePartySerializer, WritePartySerializer
from siteapp.models import Party
# from api.siteapp.filters.parties import PartyFilter

class PartyViewSet(ReadWriteViewSet):
    queryset = Party.objects.all()
    
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)

    serializer_classes = SerializerClasses(retrieve=SimplePartySerializer,
                                           list=SimplePartySerializer,
                                           create=WritePartySerializer,
                                           update=WritePartySerializer,
                                           destroy=WritePartySerializer)

    def search(self, request, keyword):
        return Q(name__icontains=keyword)