from django.conf.urls import include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

# import controls.views
from . import views_api

urlpatterns = [
    url(r'^(?P<system_id>.*)/assessment/new$', views_api.manage_system_assessment_result_api, name="new_system_assessment_result_api"),
]
