from django.db.models import Q

from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from siteapp.models import User
from api.siteapp.serializers.users import UserProfileRead
from api.siteapp.serializers.users import UserProfileWrite
from api.siteapp.serializers.users import SimpleUserSerializer

from api.base.views.base import BaseViewSet
from api.base.views.base import SerializerClasses
from api.base.views.mixins import CustomListModelMixin
from api.base.views.mixins import CustomSearchModelMixin
from api.base.views.mixins import CustomUpdateModelMixin

class UsersViewSet(BaseViewSet,
                   CustomSearchModelMixin,
                   CustomUpdateModelMixin,
                   CustomListModelMixin):
    ROLLUP = {
        # "staff_count": Q(is_staff=True)
    }
    search_fields = ['username']
    filter_backends = (filters.SearchFilter,)

    queryset = User.objects.all()
    serializer_classes = SerializerClasses(list=UserProfileRead,
                                           update=UserProfileWrite,
                                           retrieve=UserProfileRead,
                                           profile=UserProfileRead)

    def search(self, request, keyword):
        return Q(username__icontains=keyword)

    @action(methods=['GET', ], detail=False)
    def profile(self, request, **kwargs):
        serializer = self.get_serializer_class()
        data = serializer(request.user).data
        return Response(data)