from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import itsystems.views

urlpatterns = [
    url(r'^hello$', itsystems.views.index, name="hello"),
]
