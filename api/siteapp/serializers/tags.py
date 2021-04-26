from api.base.serializers.base import BaseSerializer
from api.base.serializers.types import ReadOnlySerializer
from siteapp.models import Tag


class TagSerializer(BaseSerializer):
    class Meta:
        model = Tag
        fields = ['label', 'system_created']


