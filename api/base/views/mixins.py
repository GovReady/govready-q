import abc
from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response


class CustomCreateModelMixin(CreateModelMixin):
    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class('create')
        serializer = self.get_serializer(serializer_class, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer_class = self.get_serializer_class('retrieve')
        self.kwargs['pk'] = instance.id
        obj = self.get_object(serializer_class)  # Adds the joins
        serializer = self.get_serializer(serializer_class, obj)
        data = serializer.data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CustomListModelMixin(ListModelMixin):
    def paginate(self, queryset, rollup=None):
        page = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class('list')
        serializer = self.get_serializer(serializer_class, page, many=True)
        data = self.get_paginated_response(serializer.data)
        data.data.update({"rollup": rollup})
        return data

    def dotstyle(self, dict):
        retdict = {}
        for key, value in dict.items():
            retdict[key.replace(".", "__")] = value
        return retdict

    def get_rollup(self, request, queryset):
        rollup = {}
        if True if request.query_params.get("rollup", False) in [
            "True", "true", "t", "T"] else False:
            for key, filter_ in self.ROLLUP.items():
                rollup[key] = queryset.filter(filter_).aggregate(count=Count('id'))['count']
        return rollup

    def list(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class('list')
        queryset = self.get_queryset(serializer_class=serializer_class)
        if not kwargs.pop('skip_ordering', False):
            queryset = self.filter_queryset(queryset)

        post_filter = kwargs.get('post_filter')
        if post_filter:
            queryset = queryset.filter(post_filter)

        rollup = self.get_rollup(request, queryset)

        return self.paginate(queryset=queryset, rollup=rollup)


class CustomSearchModelMixin(object):

    @abc.abstractmethod
    def search(self, request, keyword):
        pass

    def _search(self, request):
        keyword = request.GET.get('keyword')
        if keyword:
            return self.search(request, keyword)

    def list(self, request, *args, **kwargs):
        return super().list(request, post_filter=self._search(request), *args, **kwargs)


class CustomRetrieveModelMixin(RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class('retrieve')
        instance = self.get_object(serializer_class=serializer_class)
        serializer = self.get_serializer(serializer_class, instance)
        data = serializer.data
        return Response(data)


class CustomUpdateModelMixin:
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer_class = self.get_serializer_class('update')
        instance = self.get_object(serializer_class=serializer_class)
        serializer = self.get_serializer(
            serializer_class, instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        obj = self.get_object(serializer_class)  # Adds the joins
        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, obj)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        data = serializer.data
        return Response(data)

    def perform_update(self, serializer):
        return serializer.save()


class CustomDestroyModelMixin(DestroyModelMixin):

    def destroy(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class('destroy')
        instance = self.get_object(serializer_class=serializer_class)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


