from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Role


class SimpleRoleSerializer(ReadOnlySerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'title', 'short_name', 'description']

class WriteRoleSerializer(WriteOnlySerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'title', 'short_name', 'description']
