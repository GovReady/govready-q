from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import siteapp.views as views

urlpatterns = [
    url(r"^$", views.homepage),

    # apps
    url(r"^tasks/", include("guidedmodules.urls")),
    url(r"^discussion/", include("discussion.urls")),

    # projects
    url(r'^new-project$', views.new_project),
    url(r'^projects/(\d+)/_delete$', views.delete_project, name="delete_project"),
    url(r'^projects/(\d+)/(?:[\w\-]+)$', views.project),

    # invitations
    url(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
    url(r'^invitation/_cancel$', views.cancel_invitation, name="cancel_invitation"),
    url(r'^invitation/accept/(?P<code>.*)$', views.accept_invitation, name="accept_invitation"),

    # auth
    url(r'^accounts/', include('allauth.urls')),

    # has to be repeated here for the reverse() to work
    url(r'^user-media', include('dbstorage.urls')),
]

import notifications.urls
urlpatterns += [
    url('^user/notifications/', include(notifications.urls, namespace='notifications')),
    url('^_mark_notifications_as_read', views.mark_notifications_as_read),
]
