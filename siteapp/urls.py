from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import siteapp.views

urlpatterns = [
    url(r'^$', siteapp.views.homepage),

    url(r'^admin/', include(admin.site.urls)),
]
