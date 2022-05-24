from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers
from rest_framework import serializers
from siteapp.views import UserViewSet
from siteapp.views import ProjectViewSet

from .model_mixins.tags import build_tag_urls
from .models import Project

admin.autodiscover()

import siteapp.views as views
import siteapp.views_landing as views_landing
import siteapp.views_health as views_health
from .good_settings_helpers import signup_wrapper
from .settings import *

urlpatterns = [
    url(r"^warningmessage/$", views.banner, name="banner"),
    url(r"^(?![\s\S])$", views.home_user, name="home_user"),
    url(r"^login$", views.homepage, name="homepage"),
    url(r"^(privacy|terms-of-service|love-assessments)$", views.shared_static_pages, name="privacy_terms_love"),

    url(r'^api/v1/projects/(?P<project_id>\d+)/answers$', views_landing.project_api),
    url(r'^media/users/(\d+)/photo/(\w+)', views_landing.user_profile_photo),

    # incoming email hook for responses to notifications
    url(r'^notification_reply_email_hook$', views_landing.notification_reply_email_hook, name='notifications'),

    # NLP
    url(r"^nlp/", include("nlp.urls")),

    # Django rest framework
    # path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Django admin site
    url(r'^admin/', admin.site.urls),
    url(r'^media/', include('dbstorage.urls')),
    # apps
    url(r"^tasks/", include("guidedmodules.urls")),
    url(r"^discussion/", include("discussion.urls")),

    # Controls and Systems
    url(r"^system/", include("controls.urls")),
    url(r"^systems/", include("controls.urls")),
    url(r"^api/v1/systems/", include("controls.urls_api")),
    url(r"^controls/", include("controls.urls")),

    # app store
    url(r'^store$', views.apps_catalog, name="store"),
    url(r'^store/app/(?P<appversion_id>.*)/modules$', views.apps_catalog_item_modules, name='apps_catalog_item_modules'),
    # url(r'^store/app/(?P<appversion_id>.*)/clone$', views.apps_catalog_item_clone, name='apps_catalog_item_clone'),
    url(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)/zip$', views.apps_catalog_item_zip),
    url(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

    # app store
    url(r'^library$', views.apps_catalog),
    url(r'^library/(?P<source_slug>.*)/(?P<app_name>.*)/zip$', views.apps_catalog_item_zip),
    url(r'^library/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

    # profile
    url(r'account/settings$', views.account_settings, name="account_settings"),

    # projects
    url(r"^projects$", views.ProjectList.as_view(), name="projects"),
    url(r"^projects/lifecycle$", views.project_list_lifecycle, name="projects_lifecycle"),
    url(r'^projects/(?P<project_id>.*)/__edit$', views.project_edit, name="edit_project"),
    url(r'^projects/(?P<project_id>.*)/__edit_security_obj$', views.project_security_objs_edit, name="edit_project_security_objs"),
    url(r'^projects/(\d+)/__delete$', views.delete_project, name="delete_project"),
    url(r'^projects/(\d+)/__admins$', views.make_revoke_project_admin, name="make_revoke_project_admin"),
    url(r'^projects/(\d+)/__export$', views.export_project_questionnaire, name="export_project_questionnaire"),
    url(r'^projects/(\d+)/__import$', views.import_project_questionnaire, name="import_project_questionnaire"),
    url(r'^projects/(\d+)/__upgrade$', views.upgrade_project, name="upgrade_project"),
    url(r'^projects/(\d+)/__move$', views.move_project, name="move_project"),
    *build_tag_urls(r"^projects/(\d+)/", model=Project),  # Tag Urls
    url(r'^projects/(\d+)/assets/(\d+)/__update$', views.update_project_asset,
        name="update_project_assets"),
    url(r'^projects/(\d+)/$', views.project, name="view_project_id"),
    url(r'^projects/(\d+)/(?:[\w\-]+)()$', views.project, name="view_project"), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/settings)$', views.project_settings, name="project_settings"),
    url(r'^projects/(\d+)/(?:[\w\-]+)(/startapps)$', views.project_start_apps),
    # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/list)$', views.project_list_all_answers),
    # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/outputs)$', views.project_outputs),
    # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/api)$', views.project_api),
    # must be last because regex matches some previous URLs

    # portfolios
    url(r'^portfolios$', views.portfolio_list, name="list_portfolios"),
    url(r'^portfolios/new$', views.new_portfolio, name='new_portfolio'),
    url(r'^portfolios/(?P<pk>.*)/delete$', views.delete_portfolio, name="delete_portfolio"),
    url(r'^portfolios/(?P<pk>.*)/edit$', views.edit_portfolio, name="edit_portfolio"),
    url(r'^portfolios/(?P<pk>.*)/projects$', views.portfolio_projects, name="portfolio_projects"),
    url(r'^portfolio/update_permissions', views.update_permissions, name="update_permissions"),

    # org groups
    url(r'^groups$', views_landing.org_groups),
    url(r'^groups/new$', views_landing.new_org_group),
    url(r"^(?P<org_slug>.*)/projects$", views_landing.org_group_projects, name='org_projects'),

    # api
    url(r'^api-keys$', views.show_api_keys, name="show_api_keys"),

    # invitations
    url(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
    url(r'^invitation/_cancel$', views.cancel_invitation, name="cancel_invitation"),
    url(r'^invitation/accept/(?P<code>.+)$', views.accept_invitation, name="accept_invitation"),

    # support
    url(r'^support$', views.support, name="support"),

    # administration
    url(r'^settings$', views.organization_settings),
    url(r'^settings/_save$', views.organization_settings_save),

    # health
    url(r'^health/$', views_health.index),
    url(r'^health/check-system$', views_health.check_system),
    url(r'^health/check-vendor-resources$', views_health.check_vendor_resources),
    url(r'^health/list-vendor-resources$', views_health.list_vendor_resources),
    url(r'^health/load-base/(?P<args>.*)$', views_health.load_base),
    url(r'^health/request-headers$', views_health.request_headers),
    url(r'^health/request$', views_health.request),
    url(r'^health/debug$', views.debug, name="debug"),

    # tags
    url(r'^tags/_save$', views.create_tag),
    url(r'^tags/(\d+)/_delete$', views.delete_tag),
    url(r'^tags/$', views.list_tags),

    # Session
    url(r'session_security/', include('session_security.urls')),
]

urlpatterns += [url(r'^api/v2/', include('api.urls'))]
urlpatterns += [url(r'^integrations/', include('integrations.urls'))]

if settings.OKTA_CONFIG or settings.OIDC_CONFIG:
    urlpatterns += [
        path('oidc/', include('mozilla_django_oidc.urls')),
        url(r'^accounts/logout/$', views.logged_out, name="logged_out"),
        re_path(r'^accounts/login/$', RedirectView.as_view(url='/oidc/authenticate', permanent=False), name='login2')
    ]

if 'django.contrib.auth.backends.ModelBackend' in settings.AUTHENTICATION_BACKENDS:
    # If username/pwd logins are enabled, add the login pages.
    urlpatterns += [
        # auth
        # next line overrides signup with our own view so we can monitor signup attempts, can comment out to go back to allauth's functionality
        url(r'^accounts/signup/', signup_wrapper, name="account_signup"),
        # Disregard re-routing login to home page. Instead, use custom templates to style aullauth templates
        # Necessary to keep existing routing in place to support links from invitation acceptance page
        # and proper routing of "NEXT" url to project after after accepting invitation
        # login button will redirect to the homepage with a login form
        url(r'^accounts/', include('allauth.urls')),
    ]

import notifications.urls

urlpatterns += [
    url('^user/notifications/', include(notifications.urls, namespace='notifications')),
    url('^_mark_notifications_as_read', views.mark_notifications_as_read),
]

# Enterprise Single Sign On
# if SSO Proxy enabled, add-in route to `/accounts/logout/` which comes from Django's account
# module but is not present from Django when SSO Proxy enabled
if environment.get("trust-user-authentication-headers"):
    print("settings.PROXY_AUTHENTICATION_USER_HEADER enabled. Catching route accounts/logout/")

    urlpatterns += [
        url(r'^accounts/logout/$', views.sso_logout, name="sso-logout")
    ]
