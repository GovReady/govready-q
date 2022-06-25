from rest_framework import serializers

from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.import_record import SimpleImportRecordSerializer
from api.siteapp.serializers.organizations import DetailedOrganizationSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from guidedmodules.models import AppSource, AppVersion, AppInput


class SimpleAppSourceSerializer(ReadOnlySerializer):
    class Meta:
        model = AppSource
        fields = ['is_system_source', 'slug', 'spec', 'trust_assets', 'available_to_all',
                  'available_to_all_individuals', 'extra']


class DetailedAppSourceSerializer(SimpleAppSourceSerializer):
    available_to_orgs = DetailedOrganizationSerializer(many=True)
    available_to_individual = SimpleUserSerializer(many=True)

    class Meta:
        model = AppSource
        fields = SimpleAppSourceSerializer.Meta.fields + ['available_to_orgs', 'available_to_individual']


class SimpleAppVersionSourceSerializer(ReadOnlySerializer):
    catalog_metadata = serializers.JSONField()
    asset_paths = serializers.JSONField()

    class Meta:
        model = AppVersion
        fields = ['appname', 'system_app', 'catalog_metadata', 'version_number', 'version_name', 'input_paths',
                  'trust_inputs', 'asset_paths', 'trust_assets', 'show_in_catalog']


class DetailedAppVersionSerializer(SimpleAppVersionSourceSerializer):
    source = DetailedAppSourceSerializer()
    input_artifacts = SimpleImportRecordSerializer(many=True)
    asset_files = serializers.SerializerMethodField()  # Circular Dependency
    input_files = serializers.SerializerMethodField()  # Circular Dependency

    def get_asset_files(self, obj):
        from api.guidedmodules.serializers.modules import DetailedModuleAssetSerializer
        return DetailedModuleAssetSerializer(obj, many=True)

    def get_input_files(self, obj):
        from api.guidedmodules.serializers.app import DetailedAppInputSerializer
        return DetailedAppInputSerializer(obj, many=True)

    class Meta:
        model = AppVersion
        fields = SimpleAppVersionSourceSerializer.Meta.fields + ['source', 'input_files', 'input_artifacts',
                                                                 'asset_files']


class SimpleAppInputSourceSerializer(ReadOnlySerializer):
    class Meta:
        model = AppInput
        fields = ['input_name', 'content_hash', 'file']


class DetailedAppInputSerializer(SimpleAppInputSourceSerializer):
    source = DetailedAppSourceSerializer()
    app = DetailedAppVersionSerializer()

    class Meta:
        model = AppInput
        fields = SimpleAppInputSourceSerializer.Meta.fields + ['source', 'app']
