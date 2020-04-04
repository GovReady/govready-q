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
    url(r'^800-53/(?P<ctlid>.*)/$', views.control1, name="control_info"),
    # url(r'^_delete_task$', guidedmodules.views.delete_task, name="delete_task"),
]
