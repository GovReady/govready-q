from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

import siteapp.views_landing as views_landing
import guidedmodules.views

urlpatterns = [
    url(r"^$", views_landing.homepage),
    url(r"^about/", views_landing.aboutpage),

    # serve user file uploads from the main domain because the raw
    # storage data is not associated with an organization
    url(r'^user-media', include('dbstorage.urls')),

    # analytis, which are available here and on organization subdomains
    url(r'^tasks/analytics$', guidedmodules.views.analytics),

    # incoming email hook for responses to notifications
    url(r'^notification_reply_email_hook$', views_landing.notification_reply_email_hook),

    # admin site
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG: # also in non-landing urls.py
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug_toolbar__/', include(debug_toolbar.urls)),
    ]
