from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.users import SimpleUserSerializer
from siteapp.models import User


class UsersViewSet(ReadOnlyViewSet):
    ROLLUP = {
        # "staff_count": Q(is_staff=True)
    }
    queryset = User.objects.all()
    serializer_classes = SerializerClasses(retrieve=SimpleUserSerializer,
                                           list=SimpleUserSerializer)
