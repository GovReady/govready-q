from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from controls.models import Element
from siteapp.model_mixins.tags import TagView, build_tag_urls

admin.autodiscover()

from django.views.decorators.csrf import csrf_exempt

import controls.views
from nlp import views

from siteapp.settings import *

urlpatterns = [

    url(r'^nlp_index$', views.index, name="nlp_index"),
    # url(r'^nlp_index$', views.component_library, name="component_library"),


# COPIED LINKS
    # Docs
    # url('doc/', include('django.contrib.admindocs.urls')),

    # url(r'^(?P<system_id>.*)/controls/selected/export/xacta/xlsx$', views.controls_selected_export_xacta_xslx, name="controls_selected"),

    # Catalogs
    # url(r'^$', views.catalogs),
    # url(r'^catalogs$', views.catalogs),
    # url(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),


]
