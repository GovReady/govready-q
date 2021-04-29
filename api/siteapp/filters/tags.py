from django.db.models import Q
from rest_framework_filters import filters

from api.base.filters import BaseFilterSet, FilterFields
from siteapp.models import Tag


class TagFilter(BaseFilterSet):
    id_not_in = filters.CharFilter(method='id_not_in_function')

    def id_not_in_function(self, qs, name, value):
        ids = [x.strip() for x in value.split(',')]
        return qs.filter(~Q(id__in=ids))

    class Meta:
        model = Tag
        fields = {
            "label": FilterFields.String,
            "system_created": FilterFields.Boolean
        }
