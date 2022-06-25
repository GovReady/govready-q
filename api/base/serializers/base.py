from django.db.models.query import Prefetch
from rest_framework import serializers
from rest_framework.relations import ManyRelatedField
from rest_framework.relations import PrimaryKeyRelatedField


class ForeignKeyJoin(object):
    def __init__(self, column, joins=None):
        self.column = column
        self.joins = joins

    def get_column(self):
        return self.column

    def build_joins(self):
        fks = []
        prefetches = []
        if self.joins:
            for join in self.joins:
                if isinstance(join, ForeignKeyJoin):
                    formatted = "{}__{}".format(self.column, join.column)
                    fks.append(formatted)
                    child_fks, child_prefetches = join.build_joins()
                    for fk in child_fks:
                        try:
                            if isinstance(fk, str):
                                fks.append("{}__{}".format(formatted, fk))
                            else:
                                fks.append("{}__{}".format(formatted, fk.column))
                        except:
                            pass
                    for prefetch in child_prefetches:
                        try:
                            if isinstance(fk, str):
                                prefetches.append("{}__{}".format(
                                    formatted, prefetch))
                            else:
                                prefetches.append("{}__{}".format(
                                    formatted, prefetch.prefetch_to))
                        except AttributeError:
                            raise Exception(f"Developer Action - {prefetch} incorrectly configured.")
                else:
                    formatted = "{}__{}".format(self.column, join.prefetch_to)
                    prefetches.append(formatted)

        return fks, prefetches

    def normalize_joins(self):
        fks, prefetches = self.build_joins()
        return [self.column] + fks, prefetches


class SerializerOptimizer:
    @classmethod
    def detect_related_serializer_joins(cls):
        #  Auto detects joins from Related Field Serializers
        if not hasattr(cls.__class__, '__{}__initialized'.format(cls.__name__)):
            setattr(cls.__class__, '__{}__initialized'.format(cls.__name__), True)

            if not hasattr(cls.Meta, 'joins'):
                setattr(cls.Meta, 'joins', [])
            klass = cls()
            for key in klass._readable_fields:
                serializer_fks = []
                if issubclass(klass[key.field_name]._proxy_class, PrimaryKeyRelatedField):
                    cls.Meta.joins.append(ForeignKeyJoin(key.source))
                elif issubclass(klass[key.field_name]._proxy_class, ManyRelatedField):
                    queryset = klass[key.field_name]._field.child_relation.queryset \
                        if klass[key.field_name]._field.child_relation.queryset else None

                    if queryset:
                        cls.Meta.joins.append(Prefetch(klass[key.field_name]._field.source,
                                                       queryset=klass[key.field_name]._field.child_relation.
                                                       queryset.select_related(*serializer_fks)))
                    else:
                        cls.Meta.joins.append(
                            Prefetch(klass[key.field_name]._field.source))
                else:
                    class_ = klass[key.field_name]._proxy_class
                    many = False
                    if hasattr(klass[key.field_name]._field, 'many'):
                        class_ = klass[key.field_name]._field.child.__class__
                        many = True
                    if issubclass(class_, BaseSerializer):
                        class_obj = class_()
                        class_obj.detect_related_serializer_joins()
                        if not many:
                            cls.Meta.joins.append(ForeignKeyJoin(
                                key.source, class_obj.Meta.joins))
                        else:
                            serializer_fks = []
                            serializer_m2m = []
                            for x in class_obj.Meta.joins:
                                if isinstance(x, ForeignKeyJoin):
                                    fks, prefetches = x.normalize_joins()
                                    serializer_fks += fks
                                    serializer_m2m += prefetches
                                elif isinstance(x, Prefetch):
                                    serializer_m2m.append(x)

                            cls.Meta.joins.append(Prefetch(klass[key.field_name].source, queryset=class_obj.Meta.model.
                                                           objects.select_related(
                                *serializer_fks).prefetch_related(*serializer_m2m)))

    @classmethod
    def get_joins(cls):
        cls.detect_related_serializer_joins()
        selected_related = []
        prefetch_related = []
        for item in getattr(cls.Meta, 'joins', []):
            if isinstance(item, ForeignKeyJoin):
                fks, prefetches = item.normalize_joins()
                selected_related += fks
                prefetch_related += prefetches
            elif isinstance(item, Prefetch):
                prefetch_related.append(item)
        return {'selected_related': selected_related, 'prefetch_related': prefetch_related}

    @classmethod
    def prefetch_queryset(cls, queryset):
        joins = cls.get_joins()
        return queryset.select_related(*joins['selected_related']).prefetch_related(*joins['prefetch_related'])


class BaseSerializer(SerializerOptimizer,  serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.Meta, 'fields', BaseSerializer.Meta.fields + list(self.fields))

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        return super().save(**kwargs)

    def get_related_field_from_route(self, validated_data):
        for nested_item in self.context['view'].NESTED_ROUTER_PKS:
            pk = self.context['view'].kwargs[nested_item['pk']]
            validated_data[nested_item['model_field']] = nested_item['model'].objects.get(id=pk)
        return validated_data

    def update(self, instance, validated_data):
        validated_data = self.get_related_field_from_route(validated_data)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data = self.get_related_field_from_route(validated_data)
        return super().create(validated_data)

    def delete(self, validated_data):
        validated_data = self.get_related_field_from_route(validated_data)
        return super().delete(validated_data)

    class Meta:
        abstract = True
        fields = ['id', 'created', 'updated']


