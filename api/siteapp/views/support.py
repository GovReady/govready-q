from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.support import SimpleSupportSerializer
from siteapp.models import Support


class SupportViewSet(ReadOnlyViewSet):
    queryset = Support.objects.all()
    serializer_classes = SerializerClasses(retrieve=SimpleSupportSerializer,
                                           list=SimpleSupportSerializer)
