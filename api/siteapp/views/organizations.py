from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.organizations import SimpleOrganizationSerializer, DetailedOrganizationSerializer
from siteapp.models import Organization


class OrganizationViewSet(ReadOnlyViewSet):
    queryset = Organization.objects.all()
    serializer_classes = SerializerClasses(retrieve=SimpleOrganizationSerializer,
                                           list=DetailedOrganizationSerializer)
