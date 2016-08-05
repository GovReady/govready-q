from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import siteapp.views_landing as views_landing
import guidedmodules.views

urlpatterns = [
    url(r"^$", views_landing.homepage),
    url(r"^about/", views_landing.aboutpage),

    # analytis, which are available here and on organization subdomains
    url(r'^tasks/analytics$', guidedmodules.views.analytics),

    # admin site
    url(r'^admin/', include(admin.site.urls)),
]
