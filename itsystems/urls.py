from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import itsystems.views

urlpatterns = [
    url(r'^hello$', itsystems.views.index, name="hello"),
    url(r'^(?P<pk>.*)/hosts', itsystems.views.systeminstance_hostinstances_list),
    url(r'^host/(?P<pk>.*)', itsystems.views.hostinstance),
    url(r'', itsystems.views.systeminstance_list),

]
