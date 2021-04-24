from api.base.serializers.base import BaseSerializer
from siteapp.models import User


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class UserSerializer2(BaseSerializer):
    class Meta:
        model = User
        fields = ['url', ]