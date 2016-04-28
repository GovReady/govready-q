from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import siteapp.views

urlpatterns = [
    url(r"^$", siteapp.views.homepage),

    url(r"^tasks/", include("guidedmodules.urls")),

    url(r"^account/", include("account.urls")),

    url(r'^admin/', include(admin.site.urls)),
]
