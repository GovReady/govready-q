from api.base.serializers.base import BaseSerializer


class ReadOnlySerializer(BaseSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class WriteOnlySerializer(BaseSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].write_only = True
        return fields
