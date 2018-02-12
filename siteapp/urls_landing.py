from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

import siteapp.views_landing as views_landing
import guidedmodules.views

urlpatterns = [
    url(r"^$", views_landing.homepage),
    url(r"^welcome/(?P<org_slug>.*)$", views_landing.org_welcome_page),
    url(r'^api/v1/organizations/(?P<org_slug>.*)/projects/(?P<project_id>\d+)/answers$', views_landing.project_api),
    url(r'^media/users/(\d+)/photo/(\w+)/(\w+)', views_landing.user_profile_photo),

    # analytis, which are available here and on organization subdomains
    url(r'^tasks/analytics$', guidedmodules.views.analytics),

    # incoming email hook for responses to notifications
    url(r'^notification_reply_email_hook$', views_landing.notification_reply_email_hook),

    # admin site
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG: # also in non-landing urls.py
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug_toolbar__/', include(debug_toolbar.urls)),
    ]
