from rest_framework import serializers
from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Location

class SimpleLocationSerializer(ReadOnlySerializer):
    class Meta:
        model = Location
        fields = ['title', 'address_type', 'street', 'apt', 'city', 'state', 'zipcode', 'country']

class DetailedLocationSerializer(SimpleLocationSerializer):
    class Meta:
        model = Location
        fields = SimpleLocationSerializer.Meta.fields + ['uuid', 'remarks']

class WriteLocationSerializer(WriteOnlySerializer):
    uuid = serializers.UUIDField(format='hex_verbose')
    class Meta:
        model = Location
        fields = ['uuid', 'title', 'address_type', 'street', 'apt', 'city', 'state', 'zipcode', 'country', 'remarks']
