from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.tags import TagSerializer
from siteapp.models import Tag


class TagViewSet(ReadWriteViewSet):

    queryset = Tag.objects.all()
    serializer_classes = SerializerClasses(retrieve=TagSerializer,
                                           list=TagSerializer,
                                           create=TagSerializer,
                                           update=TagSerializer,
                                           destroy=TagSerializer)
