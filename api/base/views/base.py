from dataclasses import dataclass

from django.db.models import Q
from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.core.exceptions import FieldError

from api.base.serializers.base import BaseSerializer
from api.base.serializers.types import WriteOnlySerializer, ReadOnlySerializer
from api.base.views.permissions.api_token_types import APITokenPermission
from api.utils.pagination import Pagination


@dataclass(frozen=True)
class SerializerClasses:

    def __init__(self, retrieve=None, list=None, create=None, update=None, destroy=None, **kwargs):
        message = "Developer action - Cannot use a {} to write.  Use a different serializer that can {} " \
                  "in `serializer_classes` "
        if retrieve and issubclass(retrieve, WriteOnlySerializer):
            raise Exception(f"{message.format('WriteOnlySerializer', 'retrieve')}")
        if list and issubclass(list, WriteOnlySerializer):
            raise Exception(f"{message.format('WriteOnlySerializer', 'read')}")
        if create and issubclass(create, ReadOnlySerializer):
            raise Exception(f"{message.format('ReadOnlySerializer', 'create')}")
        if update and issubclass(update, ReadOnlySerializer):
            raise Exception(f"{message.format('ReadOnlySerializer', 'update')}")
        if destroy and issubclass(destroy, ReadOnlySerializer):
            raise Exception(f"{message.format('ReadOnlySerializer', 'destroy')}")
        object.__setattr__(self, 'retrieve', retrieve)
        object.__setattr__(self, 'list', list)
        object.__setattr__(self, 'create', create)
        object.__setattr__(self, 'update', update)
        object.__setattr__(self, 'destroy', destroy)
        for key, value in kwargs.items():
            if not issubclass(value, BaseSerializer):
                raise Exception("Developer action - Serializer must inherit from BaseSerializer")
            object.__setattr__(self, key, value)


@dataclass(frozen=False)
class TmpSerializerClasses:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not issubclass(value, BaseSerializer):
                raise Exception("Developer action - Serializer must inherit from BaseSerializer")
            object.__setattr__(self, key, value)


class BaseViewSet(GenericViewSet):
    __permission_classes = (IsAuthenticated, APITokenPermission)
    pagination_class = Pagination
    NESTED_ROUTER_PKS = []
    ordering = ('-created',)
    ordering_fields = '__all__'
    ROLLUP = {}  # Include Django ORM syntax to get rollup on values

    @property
    def permission_classes(self):
        return self.__permission_classes

    @permission_classes.setter
    def permission_classes(self, permissions):
        if permissions is list:
            self.permission_classes = permissions + (IsAuthenticated,)
        else:
            self.permission_classes = (IsAuthenticated, permissions)

    serializer_classes = None

    def __init__(self, *args, **kwargs):
        self.serializer_classes_tmp = TmpSerializerClasses()
        super().__init__(*args, **kwargs)

    def serializer_class_override(self, serializer_type, serializer_class):
        self.serializer_classes_tmp = TmpSerializerClasses()
        setattr(self.serializer_classes_tmp, serializer_type, serializer_class)

    def get_serializer_class(self, action=None):
        serializer_class = None
        if not action:
            action = self.action
        if hasattr(self.serializer_classes_tmp, action) and getattr(self.serializer_classes_tmp, action):
            serializer_class = getattr(self.serializer_classes_tmp, action)
        elif hasattr(self.serializer_classes, action):
            serializer_class = getattr(self.serializer_classes, action)
        if not serializer_class:
            raise NotImplementedError("'%s' should include `serializer_classes` attribute %s. "
                                      "Ex: SerializerClasses(%s='<serializer>')." % (self.__class__.__name__,
                                                                                     action, action))
        return serializer_class

    def get_serializer(self, serializer=None, *args, **kwargs):
        if not serializer:
            serializer = self.get_serializer_class()
        if not serializer:
            return super().get_serializer()
        else:
            kwargs['context'] = self.get_serializer_context()
        return serializer(*args, **kwargs)

    def get_queryset(self, queryset=None, serializer_class=None):
        if queryset is None:
            queryset = self.queryset
        exclude_ids = self.request.query_params.get("exclude")
        if exclude_ids:
            queryset = queryset.filter(~Q(id__in=exclude_ids.split(',')))
        if not serializer_class:
            try:
                serializer_class = self.get_serializer_class('list')
            finally:
                if not serializer_class:
                    raise NotImplementedError(
                        "Developer Action - Make sure you set `serializer_classes` values.")
        queryset = serializer_class.prefetch_queryset(queryset)

        if self.NESTED_ROUTER_PKS:
            for item in self.NESTED_ROUTER_PKS:
                if self.kwargs.get(item['pk']):
                    if '.' in item['model_field'] or \
                            isinstance(getattr(queryset.model, item['model_field']), ManyToManyDescriptor):
                        queryset = queryset.filter(Q(**{"{}".format(item['model_field'].replace('.', '__')):
                                                        self.kwargs[item['pk']]}))
                    else:
                        try:
                            queryset = queryset.filter(
                                Q(**{"{}_id".format(item['model_field']): self.kwargs[item['pk']]}))
                        except FieldError:
                            # Occurs on One to One relationship.  Can ignore for now - todo later
                            pass
            return queryset
        return queryset.distinct()

    def get_object(self, serializer_class=None):
        if not serializer_class:
            serializer_class = self.get_serializer_class()
        queryset = self.get_queryset(serializer_class=serializer_class)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def validate_serializer_and_get_object(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(None, instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return instance, serializer.validated_data
