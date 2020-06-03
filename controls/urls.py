from django.conf.urls import include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

import controls.views
from . import views

from siteapp.settings import *

urlpatterns = [
    url(r'^test$', views.test),
    
    # Catalogs
    url(r'^$', views.catalogs),
    url(r'^catalogs$', views.catalogs),
    url(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),

    # Systems
    url(r'^(?P<system_id>.*)/controls/selected/export/xacta/xlsx$', views.controls_selected_export_xacta_xslx, name="controls_selected"),
    url(r'^(?P<system_id>.*)/controls/selected$', views.controls_selected, name="controls_selected"),
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/compare$', views.editor_compare, name="control_compare"),
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)$', views.editor, name="control_editor"),
    url(r'^smt/_save/$', views.save_smt),
    url(r'^smt/_delete/$', views.delete_smt),
    url(r'^(?P<system_id>.*)/components/selected$', views.components_selected, name="components_selected"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)$', views.system_element, name="system_element"),

    # Controls
    url(r'^catalogs/(?P<catalog_key>.*)/group/(?P<g_id>.*)', views.group, name="control_group"),
    url(r'^catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)', views.control, name="control_info"),

    # Components

]
