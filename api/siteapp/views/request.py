from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.request import SimpleRequestSerializer, WriteRequestSerializer
from siteapp.models import Request
# from api.siteapp.filters.requests import RequestFilter

class RequestViewSet(ReadWriteViewSet):
    queryset = Request.objects.all()

    serializer_classes = SerializerClasses(retrieve=SimpleRequestSerializer,
                                           list=SimpleRequestSerializer,
                                           create=WriteRequestSerializer,
                                           update=WriteRequestSerializer,
                                           destroy=WriteRequestSerializer)
    # filter_class = RequestFilter