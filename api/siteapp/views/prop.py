from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.prop import SimplePropSerializer, WritePropSerializer
from controls.models import Prop

class ProposalViewSet(ReadWriteViewSet):
    queryset = Prop.objects.all()

    serializer_classes = SerializerClasses(retrieve=SimplePropSerializer,
                                           list=SimplePropSerializer,
                                           create=WritePropSerializer,
                                           update=WritePropSerializer,
                                           destroy=WritePropSerializer,
                                           )
    # filter_class = PropFilter

