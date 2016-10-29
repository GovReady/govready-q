# nothing here

from .settings import *

INSTALLED_APPS += [
    'debug_toolbar',

    'htmlemailer',
    'notifications',
    'dbstorage',

    'siteapp',
    'guidedmodules',
    'discussion',
]

MIDDLEWARE_CLASSES += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'siteapp.middleware.OrganizationSubdomainMiddleware',
]

AUTHENTICATION_BACKENDS += ['siteapp.models.DirectLoginBackend']

INTERNAL_IPS = ['127.0.0.1'] # for django_debug_toolbar

# ALLWOED_HOSTS is set based on environment['host'], which gives us
# our landing page domain. Also allow all subdomains of the organization
# parent domain.
ORGANIZATION_PARENT_DOMAIN = environment.get('organization-parent-domain', 'localhost')
ALLOWED_HOSTS += ['.' + ORGANIZATION_PARENT_DOMAIN]

SERVER_EMAIL = "GovReady Q <q@mg.govready.com>"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'

MODULES_PATH = environment.get('modules-path', 'modules')

GOVREADY_CMS_API_AUTH = environment.get('govready_cms_api_auth')
