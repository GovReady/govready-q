from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import itsystems.views

urlpatterns = [
    url(r'^hello$', itsystems.views.index, name="hello"),
    url(r'^new$', itsystems.views.new_systeminstance),
    url(r'^hosts/new$', itsystems.views.new_hostinstance),
    url(r'^hosts/list$', itsystems.views.hostinstance_list),
    url(r'^agent/list$', itsystems.views.agent_list),
    url(r'^(?P<pk>.*)/hosts', itsystems.views.systeminstance_hostinstances_list,name="systeminstance_hostinstances_list"),
    url(r'^agents/new$', itsystems.views.new_agent),
    url(r'^agentservice/new$', itsystems.views.new_agentservice),
    url(r'^hosts/(?P<pk>.*)', itsystems.views.hostinstance),
    url(r'', itsystems.views.systeminstance_list),

]
