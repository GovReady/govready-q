from rest_framework.decorators import action
from rest_framework.response import Response

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet, ReadWriteViewSet
from api.controls.serializers.element import DetailedElementSerializer, SimpleElementSerializer, \
    WriteElementTagsSerializer, ElementPermissionSerializer, UpdateElementPermissionSerializer
from controls.models import Element
from siteapp.models import User

class ElementViewSet(ReadOnlyViewSet):
    queryset = Element.objects.all()
    serializer_classes = SerializerClasses(retrieve=DetailedElementSerializer,
                                           list=SimpleElementSerializer,
                                           tags=WriteElementTagsSerializer)

    @action(detail=True, url_path="tags", methods=["PUT"])
    def tags(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        element.tags.clear()
        element.tags.add(*validated_data['tags'])
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

class ElementWithPermissionsViewSet(ReadWriteViewSet):
    # NESTED_ROUTER_PKS = [{'pk': 'modules_pk', 'model_field': 'module', 'model': Module}]
    queryset = Element.objects.all()
    # ordering = ('definition_order',)
    serializer_classes = SerializerClasses(retrieve=ElementPermissionSerializer,
                                           list=ElementPermissionSerializer,
                                           create=UpdateElementPermissionSerializer,
                                           update=UpdateElementPermissionSerializer,
                                           destroy=UpdateElementPermissionSerializer,
                                           assign_role=UpdateElementPermissionSerializer)

    @action(detail=True, url_path="assign_role", methods=["PUT"])
    def assign_role(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)

        # assign permissions to user on element
        #calling function of that element

        user_permissions = []
        perm_user = {}

        for key, value in validated_data.items():
            perm_user = value['user']
            if(value['add']):
                user_permissions.append('add_element')
            if(value['change']):
                user_permissions.append('change_element')
            if(value['delete']):
                user_permissions.append('delete_element')
            if(value['view']):
                user_permissions.append('view_element')

        user = User.objects.get(id=perm_user['id'])
        element.assign_user_permissions(user, user_permissions)

        element.save()
        
        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)
