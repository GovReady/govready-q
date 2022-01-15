from rest_framework import serializers

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.guidedmodules.serializers.app import DetailedAppVersionSerializer, SimpleAppSourceSerializer, SimpleAppVersionSourceSerializer
from guidedmodules.models import Module, ModuleAsset, ModuleQuestion
from rest_framework_recursive.fields import RecursiveField


class SimpleModuleSerializer(ReadOnlySerializer):
    spec = serializers.SerializerMethodField()

    def get_spec(self, obj):
        return dict(obj.spec)

    class Meta:
        model = Module
        fields = ['module_name', 'spec']

class DetailedModuleSerializer(SimpleModuleSerializer):
    source = SimpleAppSourceSerializer()
    app = DetailedAppVersionSerializer()
    superseded_by = RecursiveField(required=False, allow_null=True)

    class Meta:
        model = Module
        fields = SimpleModuleSerializer.Meta.fields + ['source', 'app', 'superseded_by']


class SimpleModuleAssetSerializer(ReadOnlySerializer):
    class Meta:
        model = ModuleAsset
        fields = ['content_hash', 'file', 'extra']


class DetailedModuleAssetSerializer(SimpleModuleAssetSerializer):
    source = SimpleAppSourceSerializer()

    class Meta:
        model = ModuleAsset
        fields = SimpleModuleAssetSerializer.Meta.fields + ['source']


class SimpleModuleQuestionSerializer(ReadOnlySerializer):
    spec = serializers.JSONField()

    class Meta:
        model = ModuleQuestion
        fields = ['key', 'definition_order', 'spec']


class DetailedModuleQuestionSerializer(SimpleModuleQuestionSerializer):

    class Meta:
        model = ModuleQuestion
        fields = SimpleModuleQuestionSerializer.Meta.fields


class ModuleQuestionListSerializer(SimpleModuleQuestionSerializer):
    answer_type_module = DetailedModuleSerializer()

    class Meta:
        model = ModuleQuestion
        fields = SimpleModuleQuestionSerializer.Meta.fields

class ModuleReadSerializer(ReadOnlySerializer):
    spec = serializers.JSONField()
    app = SimpleAppVersionSourceSerializer()
    questions = SimpleModuleQuestionSerializer(many=True)

    class Meta:
        model = Module
        fields = ['module_name', 'spec', 'app', 'questions']

class CreateModuleQuestionSerializer(WriteOnlySerializer):
    spec = serializers.JSONField()
    key = serializers.CharField()
    definition_order = serializers.IntegerField()

    # module_id = serializers.PrimaryKeyRelatedField(source='module', allow_null=False, queryset=Module.objects)

    class Meta:
        model = ModuleQuestion
        fields = ['key', 'definition_order', 'spec'
        ]

