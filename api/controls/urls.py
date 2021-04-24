from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.controls.views.element import ElementViewSet

router = routers.DefaultRouter()
router.register(r'elements', ElementViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
