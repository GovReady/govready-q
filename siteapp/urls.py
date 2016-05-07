from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import siteapp.views

urlpatterns = [
    url(r"^$", siteapp.views.homepage),

    url(r"^tasks/", include("guidedmodules.urls")),

	url('^login/$', siteapp.views.login_view, name='login'),
    url('^', include('django.contrib.auth.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
