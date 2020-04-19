from django.conf.urls import include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

import controls.views
from . import views

from siteapp.settings import *


urlpatterns = [
    url(r'^test$', views.test),
    url(r'^$', views.test),
    url(r'^800-53/(?P<cl_id>.*)/$', views.control1, name="control_info"),
    url(r'^800-53/(?P<cl_id>.*)/editor$', views.editor, name="control_editor"),

    url(r'^smt/_save/$', views.save_smt),

]
