from rest_framework.decorators import action
from rest_framework.response import Response

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
                                           destroy=WriteRequestSerializer,)
                                        #    requestList=WriteRequestSerializer)
    # filter_class = RequestFilter

    # @action(detail=True, url_path="requestList", methods=["PUT"])
    # def appointments(self, request, **kwargs):
    #     req, validated_data = self.validate_serializer_and_get_object(request)

    #     for key, value in validated_data.items():
    #         req.add_appointments(value)
    #     req.save()

    #     serializer_class = self.get_serializer_class('retrieve')
    #     serializer = self.get_serializer(serializer_class, req)
    #     return Response(serializer.data)
