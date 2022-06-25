from django.db.models import Q
from rest_framework import filters

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.role import SimpleRoleSerializer, WriteRoleSerializer
from siteapp.models import Role
# from api.siteapp.filters.roles import RoleFilter

class RoleViewSet(ReadWriteViewSet):
    queryset = Role.objects.all()
    
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    
    serializer_classes = SerializerClasses(retrieve=SimpleRoleSerializer,
                                           list=SimpleRoleSerializer,
                                           create=WriteRoleSerializer,
                                           update=WriteRoleSerializer,
                                           destroy=WriteRoleSerializer)

    def search(self, request, keyword):
        return Q(title__icontains=keyword)