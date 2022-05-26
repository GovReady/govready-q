from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r"^identify$", views.integration_identify, name='integration_identify'),
    url(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name='integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    url(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name='integration_endpoint'),
]
