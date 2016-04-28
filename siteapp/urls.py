from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [
    url(r'^$', guidedmodules.views.next_question),

    url(r"^account/", include("account.urls")),

    url(r'^admin/', include(admin.site.urls)),
]
