from django.conf.urls import include, url
from . import views

INTEGRATION_NAME = 'csam'

urlpatterns = [

    url(r"^$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    url(r"^identify$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    url(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    url(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name=f'{INTEGRATION_NAME}_integration_endpoint_post'),

    url(r"^get_system_info_test/(?P<system_id>.*)$", views.get_system_info, name=f'{INTEGRATION_NAME}_get_system_info_test'),
    url(r"^update_system_description_test/(?P<system_id>.*)$", views.update_system_description_test,
        name=f'{INTEGRATION_NAME}_update_system_description_test'),
    url(r"^update_system_description$", views.update_system_description,
        name=f'{INTEGRATION_NAME}_update_system_description'),

    url(r"^get_multiple_system_info/(?P<system_id_list>.*)$", views.get_multiple_system_info, name=f'{INTEGRATION_NAME}_get_multiple_system_info'),

    url(r"^local/system/(?P<system_id>.*)$", views.get_paired_remote_system_info_using_local_system_id, name=f'{INTEGRATION_NAME}_csam_system_info'),

    url(r"^create_system_from_remote/$", views.create_system_from_remote, name=f'{INTEGRATION_NAME}_create_system_from_remote'),
    url(r"^create_system_from_remote/(?P<remote_system_id>.*)$", views.create_system_from_remote, name=f'{INTEGRATION_NAME}_create_system_from_remote'),
    
]
