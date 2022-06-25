from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Party


class SimplePartySerializer(ReadOnlySerializer):
    class Meta:
        model = Party
        fields = ['party_type', 'name', 'short_name', 'email', 'phone_number', 'mobile_phone']

class WritePartySerializer(WriteOnlySerializer):
    class Meta:
        model = Party
        fields = ['party_type', 'name', 'short_name', 'email', 'phone_number', 'mobile_phone']
