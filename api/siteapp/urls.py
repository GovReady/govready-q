from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.siteapp.views.projects import ProjectViewSet
from api.siteapp.views.users import UsersViewSet


router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
