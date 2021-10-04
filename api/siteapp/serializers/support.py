from api.base.serializers.types import ReadOnlySerializer
from siteapp.models import Support


class SimpleSupportSerializer(ReadOnlySerializer):
    class Meta:
        model = Support
        fields = ['email', 'phone', 'text', 'url']
