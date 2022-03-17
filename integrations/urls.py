from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r"^csam/", include("integrations.csam.urls")),
    url(r"^jsonplaceholder/", include("integrations.jsonplaceholder.urls")),
]