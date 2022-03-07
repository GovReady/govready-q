from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path

from . import views

urlpatterns = [
    # url(r"^jsonplaceholder/users$", views.jsonplaceholders_users, name='jsonplaceholders_users'),

    url(r"^(?P<integration>.*)/identify$", views.integration_identify, name='integration_identify'),
    url(r"^(?P<integration>.*)/endpoint(?P<endpoint>.*)$", views.integration_endpoint, name='integration_endpoint'),
]