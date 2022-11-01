from rest_framework import serializers
from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Address, Location

class SimpleAddressSerializer(ReadOnlySerializer):
    class Meta:
        model = Address
        fields = ['address_type', 'addr_line', 'city', 'state', 'postal_code', 'country']

class WriteAddressSerializer(ReadOnlySerializer):
    class Meta:
        model = Address
        fields = ['address_type', 'addr_line', 'city', 'state', 'postal_code', 'country']

class SimpleLocationSerializer(ReadOnlySerializer):
    # addr = SimpleAddressSerializer()
    class Meta:
        model = Location
        fields = ['title', 'address', 'urls', 'remarks']

class DetailedLocationSerializer(SimpleLocationSerializer):
    class Meta:
        model = Location
        fields = SimpleLocationSerializer.Meta.fields + ['uuid', 'remarks']


class WriteLocationSerializer(WriteOnlySerializer):
    # address = WriteAddressSerializer(required=False, many=True)
    
    class Meta:
        model = Location
        fields = ['title', 'urls', 'remarks']