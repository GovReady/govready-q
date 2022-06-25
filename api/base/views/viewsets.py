from api.base.views.base import BaseViewSet
from api.base.views.mixins import CustomCreateModelMixin, CustomRetrieveModelMixin, CustomDestroyModelMixin, \
    CustomUpdateModelMixin, CustomListModelMixin


class ReadWriteViewSet(BaseViewSet,
                       CustomCreateModelMixin,
                       CustomRetrieveModelMixin,
                       CustomUpdateModelMixin,
                       CustomDestroyModelMixin,
                       CustomListModelMixin):
    pass


class ReadOnlyViewSet(BaseViewSet,
                      CustomRetrieveModelMixin,
                      CustomListModelMixin):
    pass


class WriteOnlyViewSet(BaseViewSet,
                       CustomCreateModelMixin,
                       CustomUpdateModelMixin,
                       CustomDestroyModelMixin):
    pass


class ReadUpdateViewSet(BaseViewSet,
                        CustomRetrieveModelMixin,
                        CustomUpdateModelMixin,
                        CustomListModelMixin):
    pass
