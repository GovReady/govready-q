from rest_framework.permissions import DjangoModelPermissions

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.controls.serializers.element import DetailedElementSerializer, WriteElementSerializer
from controls.models import Element


class ElementViewSet(ReadWriteViewSet):
    permission_classes = [DjangoModelPermissions, ]

    queryset = Element.objects.all()

    serializer_classes = SerializerClasses(retrieve=DetailedElementSerializer,
                                           list=DetailedElementSerializer,
                                           create=WriteElementSerializer,
                                           update=WriteElementSerializer,
                                           destroy=WriteElementSerializer)
