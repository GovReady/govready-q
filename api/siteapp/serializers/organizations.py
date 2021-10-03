from api.base.serializers.types import ReadOnlySerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from siteapp.models import Organization, OrganizationalSetting


class SimpleOrganizationSerializer(ReadOnlySerializer):
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'extra']


class DetailedOrganizationSerializer(SimpleOrganizationSerializer):
    help_squad = SimpleUserSerializer(many=True)
    reviewers = SimpleUserSerializer(many=True)

    class Meta:
        model = Organization
        fields = SimpleOrganizationSerializer.Meta.fields + ['help_squad', 'reviewers']


class SimpleOrganizationalSettingSerializer(ReadOnlySerializer):
    class Meta:
        model = OrganizationalSetting
        fields = ['catalog_key', 'parameter_key', 'value']


class DetailedOrganizationalSettingSerializer(SimpleOrganizationalSettingSerializer):
    organization = DetailedOrganizationSerializer()

    class Meta:
        model = OrganizationalSetting
        fields = SimpleOrganizationalSettingSerializer.Meta.fields + ['organization']
