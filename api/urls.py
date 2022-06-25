from django.conf.urls import url
from django.urls import include

from api.base.urls import get_swagger_urls

urlpatterns = [
    url(r'^', include('api.controls.urls')),
    url(r'^', include('api.discussion.urls')),
    url(r'^', include('api.guidedmodules.urls')),
    url(r'^', include('api.siteapp.urls')),
] + get_swagger_urls()
