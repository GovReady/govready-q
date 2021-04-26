from api.base.serializers.types import ReadOnlySerializer
from siteapp.models import User


class SimpleUserSerializer(ReadOnlySerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff', 'notifemails_enabled']
