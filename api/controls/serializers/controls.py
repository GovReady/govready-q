from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.element import DetailedElementSerializer
from controls.models import CommonControlProvider, CommonControl, ElementCommonControl


class SimpleCommonControlProviderSerializer(ReadOnlySerializer):
    class Meta:
        model = CommonControlProvider
        fields = ['name', 'description']


class SimpleCommonControlSerializer(ReadOnlySerializer):
    class Meta:
        model = CommonControl
        fields = ['name', 'description', 'oscal_ctl_id', 'legacy_imp_smt']


class DetailedCommonControlSerializer(SimpleCommonControlSerializer):
    common_control_provider = SimpleCommonControlProviderSerializer()

    class Meta:
        model = CommonControl
        fields = SimpleCommonControlSerializer.Meta.fields + ['common_control_provider']


class SimpleElementCommonControlSerializer(ReadOnlySerializer):
    class Meta:
        model = ElementCommonControl
        fields = ['oscal_ctl_id', 'oscal_catalog_key']


class DetailedElementCommonControlSerializer(SimpleElementCommonControlSerializer):
    element = DetailedElementSerializer()
    common_control = DetailedCommonControlSerializer()

    class Meta:
        model = ElementCommonControl
        fields = SimpleElementCommonControlSerializer.Meta.fields + ['element', 'common_control']
