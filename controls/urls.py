from django.conf.urls import include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

import controls.views
from . import views

from siteapp.settings import *

urlpatterns = [
    url(r'^test$', views.test),
    
    url(r'^$', views.catalogs),
    url(r'^catalogs$', views.catalogs),
    url(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),
    
    url(r'^catalogs/(?P<catalog_key>.*)/group/(?P<g_id>.*)', views.group, name="control_group"),
    url(r'^catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/editor$', views.editor, name="control_editor"),
    url(r'^catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)', views.control, name="control_info"),
 
    url(r'^smt/_save/$', views.save_smt),
    url(r'^smt/_delete/$', views.delete_smt),

    # Systems
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/editor$', views.editor, name="control_editor"),
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/editor/compare$', views.editor_compare, name="control_editor_compare"),

]
