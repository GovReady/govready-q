from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.projects import DetailedProjectsSerializer, SimpleProjectsSerializer
from siteapp.models import Project


class ProjectViewSet(ReadOnlyViewSet):
    queryset = Project.objects.all()
    serializer_classes = SerializerClasses(retrieve=DetailedProjectsSerializer,
                                           list=SimpleProjectsSerializer)
