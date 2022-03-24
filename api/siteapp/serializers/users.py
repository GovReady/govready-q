from api.base.serializers.types import ReadOnlySerializer
from api.base.serializers.types import WriteOnlySerializer
from siteapp.models import User


class SimpleUserSerializer(ReadOnlySerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'notifemails_enabled']

class UserProfileRead(ReadOnlySerializer):
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'is_staff', 'notifemails_enabled']


class UserProfileWrite(WriteOnlySerializer):
    class Meta:
        model = User # It's a base class for all the viewsets.
        fields = ['username', 'name', 'email', 'is_staff', 'notifemails_enabled']
