from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.projects import DetailedProjectsSerializer, SimpleProjectsSerializer, \
    WriteProjectTagsSerializer
from siteapp.models import Project


class ProjectViewSet(ReadOnlyViewSet):
    queryset = Project.objects.all()
    serializer_classes = SerializerClasses(retrieve=DetailedProjectsSerializer,
                                           list=SimpleProjectsSerializer,
                                           set_tags=WriteProjectTagsSerializer)

    @action(detail=True, url_path="tags", methods=["PUT"])
    def set_tags(self, request, **kwargs):
        project, validated_data = self.validate_serializer_and_get_object(request)
        project.tags.clear()
        project.tags.add(*validated_data['tags'])
        project.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, project)
        return Response(serializer.data)
