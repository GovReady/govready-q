from django.db.models import Q
from rest_framework import filters

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.location import SimpleLocationSerializer, DetailedLocationSerializer, WriteLocationSerializer
from siteapp.models import Location

class LocationViewSet(ReadWriteViewSet):
    queryset = Location.objects.all()
    
    search_fields = ['street']
    filter_backends = (filters.SearchFilter,)

    serializer_classes = SerializerClasses(retrieve=DetailedLocationSerializer,
                                           list=SimpleLocationSerializer,
                                           create=WriteLocationSerializer,
                                           update=WriteLocationSerializer,
                                           destroy=WriteLocationSerializer,
                                        )

    def search(self, request, keyword):
        return Q(name__icontains=keyword)