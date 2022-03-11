from django.conf.urls import include, url
from . import views

urlpatterns = [
    # url(r"^jsonplaceholder/users$", views.jsonplaceholders_users, name='jsonplaceholders_users'),
    # url(r"^(?P<integration_name>.*)/identify$", views.integration_identify, name='integration_identify'),
    # url(r"^(?P<integration_name>.*)/endpoint(?P<endpoint>.*)$", views.integration_endpoint,
    #     name='integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    url(r"^csam/", include("integrations.csam.urls")),
    url(r"^jsonplaceholder/", include("integrations.jsonplaceholder.urls")),
]