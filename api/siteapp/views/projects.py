from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.projects import DetailedProjectSerializer
from siteapp.models import Project


class ProjectViewSet(ReadWriteViewSet):

    queryset = Project.objects.all()
    serializer_classes = SerializerClasses(retrieve=DetailedProjectSerializer,
                                           list=DetailedProjectSerializer,
                                           create=DetailedProjectSerializer,
                                           update=DetailedProjectSerializer,
                                           destroy=DetailedProjectSerializer)
