from api.base.serializers.types import ReadOnlySerializer


class AssetMixinSerializer(ReadOnlySerializer):
    class Meta:
        model = None
        fields = ['title', 'asset_type', 'content_hash', 'description', 'filename', 'file', 'extra', 'uuid']


