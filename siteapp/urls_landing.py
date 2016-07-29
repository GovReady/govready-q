from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import siteapp.views_landing as views_landing

urlpatterns = [
    url(r"^$", views_landing.homepage),
    url(r"^about/", views_landing.aboutpage),

    # admin site
    url(r'^admin/', include(admin.site.urls)),
]
