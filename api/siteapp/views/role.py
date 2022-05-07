from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.role import SimpleRoleSerializer, WriteRoleSerializer
from siteapp.models import Role
# from api.siteapp.filters.roles import RoleFilter

class RoleViewSet(ReadWriteViewSet):
    queryset = Role.objects.all()

    serializer_classes = SerializerClasses(retrieve=SimpleRoleSerializer,
                                           list=SimpleRoleSerializer,
                                           create=WriteRoleSerializer,
                                           update=WriteRoleSerializer,
                                           destroy=WriteRoleSerializer)
    # filter_class = RoleFilter