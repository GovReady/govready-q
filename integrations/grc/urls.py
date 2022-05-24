from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r"^identify$", views.integration_identify, name='integration_identify'),
    url(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name='integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    url(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name='integration_endpoint'),

    url(r"^get_system_info_test/(?P<system_id>.*)$", views.get_system_info, name='get_system_info_test'),
    url(r"^update_system_description_test/(?P<system_id>.*)$", views.update_system_description_test,
        name='update_system_description_test'),
    url(r"^update_system_description$", views.update_system_description,
        name='update_system_description'),

    url(r"^get_multiple_system_info/(?P<system_id_list>.*)$", views.get_multiple_system_info, name='get_multiple_system_info'),

    url(r"^system/(?P<system_id>.*)$", views.system_info, name='csam_system_info'),
    
]
