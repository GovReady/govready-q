from django.conf.urls import include, url
from . import views

INTEGRATION_NAME = "jsonplaceholder"
urlpatterns = [

    url(r"^$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    url(r"^identify$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    url(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    url(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),
]
