from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.guidedmodules.serializers.modules import ModuleReadSerializer
from guidedmodules.models import Module


class ModuleViewSet(ReadOnlyViewSet):
    queryset = Module.objects.all()
    serializer_classes = SerializerClasses(retrieve=ModuleReadSerializer,
                                           list=ModuleReadSerializer)
