from api.base.serializers.base import BaseSerializer
from siteapp.models import Tag


class TagSerializer(BaseSerializer):
    class Meta:
        model = Tag
        fields = BaseSerializer.Meta.fields + ['label', 'system_created']


