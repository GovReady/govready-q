from os import system
from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.controls.serializers.element import SimpleElementControlSerializer, DetailedElementControlSerializer
from api.controls.serializers.poam import DetailedPoamSerializer, SimplePoamSerializer, SimpleSpreadsheetPoamSerializer
from api.controls.serializers.system import DetailedSystemSerializer, SimpleSystemSerializer
from api.controls.serializers.system_assement_results import DetailedSystemAssessmentResultSerializer, \
    SimpleSystemAssessmentResultSerializer
from controls.models import System, ElementControl, SystemAssessmentResult, Poam


class SystemViewSet(ReadOnlyViewSet):
    queryset = System.objects.all()

    serializer_classes = SerializerClasses(retrieve=DetailedSystemSerializer,
                                           list=SimpleSystemSerializer)


class SystemControlsViewSet(ReadOnlyViewSet):
    queryset = ElementControl.objects.all()

    serializer_classes = SerializerClasses(retrieve=DetailedElementControlSerializer,
                                           list=SimpleElementControlSerializer)

    NESTED_ROUTER_PKS = [{'pk': 'systems_pk', 'model_field': 'element.system'}]


class SystemAssessmentViewSet(ReadOnlyViewSet):
    queryset = SystemAssessmentResult.objects.all()

    serializer_classes = SerializerClasses(retrieve=DetailedSystemAssessmentResultSerializer,
                                           list=SimpleSystemAssessmentResultSerializer)

    NESTED_ROUTER_PKS = [{'pk': 'systems_pk', 'model_field': 'system'}]


class SystemPoamViewSet(ReadOnlyViewSet):
    queryset = Poam.objects.all()

    serializer_classes = SerializerClasses(retrieve=DetailedPoamSerializer,
                                           list=SimplePoamSerializer)
                                        #    spreadsheet=SimpleSpreadsheetPoamSerializer)
    # @action(detail=True, url_path="spreadsheet", methods=["GET"])
    # def spreadsheet(self, request, **kwargs):
    #     system, validated_data = self.validate_serializer_and_get_object(request)

    #     serializer_class = self.get_serializer_class('list')
    #     serializer = self.get_serializer(serializer_class, system)
    #     return Response(serializer.data)

    NESTED_ROUTER_PKS = [{'pk': 'systems_pk', 'model_field': 'statement.consumer_element.system'}]

class SystemPoamSpreadsheetViewSet(ReadOnlyViewSet):
    queryset = System.objects.all()
    serializer_classes = SerializerClasses(
        retrieve=SimpleSpreadsheetPoamSerializer,
        list=SimpleSpreadsheetPoamSerializer)
