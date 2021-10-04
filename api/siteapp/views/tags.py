from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.filters.tags import TagFilter
from api.siteapp.serializers.tags import SimpleTagSerializer, WriteTagSerializer
from siteapp.models import Tag


class TagViewSet(ReadWriteViewSet):
    queryset = Tag.objects.all()
    serializer_classes = SerializerClasses(retrieve=SimpleTagSerializer,
                                           list=SimpleTagSerializer,
                                           create=WriteTagSerializer,
                                           update=WriteTagSerializer,
                                           destroy=WriteTagSerializer)
    filter_class = TagFilter
