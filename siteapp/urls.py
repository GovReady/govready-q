from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

import siteapp.views as views
import siteapp.views_landing as views_landing
from .good_settings_helpers import signup_wrapper

urlpatterns = [
    url(r"^$", views.homepage, name="homepage"),
    url(r"^(privacy|terms-of-service)$", views.shared_static_pages),

    url(r'^api/v1/projects/(?P<project_id>\d+)/answers$', views_landing.project_api),
    url(r'^media/users/(\d+)/photo/(\w+)', views_landing.user_profile_photo),

    # incoming email hook for responses to notifications
    url(r'^notification_reply_email_hook$', views_landing.notification_reply_email_hook),

    # Django admin site
    url(r'^admin/', admin.site.urls),

    # apps
    url(r"^tasks/", include("guidedmodules.urls")),
    url(r"^discussion/", include("discussion.urls")),

    # app store
    url(r'^store$', views.apps_catalog),
    url(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

    # projects
    url(r"^projects$", views.project_list),
    url(r'^projects/(\d+)/__rename$', views.rename_project, name="rename_project"),
    url(r'^projects/(\d+)/__delete$', views.delete_project, name="delete_project"),
    url(r'^projects/(\d+)/__admins$', views.make_revoke_project_admin, name="make_revoke_project_admin"),
    url(r'^projects/(\d+)/__export$', views.export_project, name="export_project"),
    url(r'^projects/(\d+)/__import$', views.import_project_data, name="import_project_data"),
    url(r'^projects/(\d+)/(?:[\w\-]+)()$', views.project), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/startapps)$', views.project_start_apps), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/list)$', views.project_list_all_answers), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/outputs)$', views.project_outputs), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/api)$', views.project_api), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/upgrade)$', views.project_upgrade_app), # must be last because regex matches some previous URLs

    # org groups
    url(r'^groups$', views_landing.org_groups),
    url(r'^groups/new$', views_landing.new_org_group),
    url(r"^(?P<org_slug>.*)/projects$", views_landing.org_group_projects),

    # api
    url(r'^api-keys$', views.show_api_keys, name="show_api_keys"),

    # invitations
    url(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
    url(r'^invitation/_cancel$', views.cancel_invitation, name="cancel_invitation"),
    url(r'^invitation/accept/(?P<code>.+)$', views.accept_invitation, name="accept_invitation"),

    # administration
    url(r'^settings$', views.organization_settings),
    url(r'^settings/_save$', views.organization_settings_save),
]

if 'django.contrib.auth.backends.ModelBackend' in settings.AUTHENTICATION_BACKENDS:
    # If username/password logins are enabled, add the login pages.
    urlpatterns += [
        # auth
        # next line overrides signup with our own view so we can monitor signup attempts, can comment out to go back to allauth's functionality
        url(r'^accounts/signup/', signup_wrapper, name="account_signup"),
        url(r'^accounts/', include('allauth.urls')),
    ]

import notifications.urls
urlpatterns += [
    url('^user/notifications/', include(notifications.urls, namespace='notifications')),
    url('^_mark_notifications_as_read', views.mark_notifications_as_read),
]

if settings.DEBUG: # also in urls_landing
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug_toolbar__/', include(debug_toolbar.urls)),
    ]
