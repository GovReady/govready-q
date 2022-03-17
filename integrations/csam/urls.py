from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r"^identify$", views.integration_identify, name='integration_identify'),
    url(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name='integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    url(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name='integration_endpoint'),

    url(r"^update_system_description_test/(?P<system_id>.*)$", views.update_system_description_test,
        name='integration_endpoint'),
    url(r"^update_system_description$", views.update_system_description,
        name='integration_endpoint'),
]
