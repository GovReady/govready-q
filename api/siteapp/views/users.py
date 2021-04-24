from django.db.models import Q

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.users import UserSerializer, UserSerializer2
from siteapp.models import User


class UsersViewSet(ReadOnlyViewSet):
    ROLLUP = {
        "staff_count": Q(is_staff=True)
    }
    queryset = User.objects.all()
    serializer_classes = SerializerClasses(retrieve=UserSerializer,
                                           list=UserSerializer2,
                                           test=UserSerializer)
