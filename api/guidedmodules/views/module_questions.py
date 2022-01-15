from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.guidedmodules.serializers.modules import SimpleModuleQuestionSerializer, CreateModuleQuestionSerializer
from guidedmodules.models import Module, ModuleQuestion


class ModuleQuestionViewSet(ReadWriteViewSet):
    NESTED_ROUTER_PKS = [{'pk': 'modules_pk', 'model_field': 'module', 'model': Module}]
    queryset = ModuleQuestion.objects.all()
    ordering = ('definition_order',)
    serializer_classes = SerializerClasses(retrieve=SimpleModuleQuestionSerializer,
                                           list=SimpleModuleQuestionSerializer,
                                           create=CreateModuleQuestionSerializer,
                                           update=CreateModuleQuestionSerializer,
                                           destroy=CreateModuleQuestionSerializer)

