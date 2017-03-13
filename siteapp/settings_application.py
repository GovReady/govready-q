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

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'siteapp.middleware.OrganizationSubdomainMiddleware',
    'guidedmodules.middleware.InstrumentQuestionPageLoadTimes',
]

AUTHENTICATION_BACKENDS += ['siteapp.models.DirectLoginBackend']

INTERNAL_IPS = ['127.0.0.1'] # for django_debug_toolbar

# ALLWOED_HOSTS is set based on environment['host'], which gives us
# our landing page domain. Also allow all subdomains of the organization
# parent domain.
ORGANIZATION_PARENT_DOMAIN = environment.get('organization-parent-domain', 'localhost')
ALLOWED_HOSTS += ['.' + ORGANIZATION_PARENT_DOMAIN]
REVEAL_ORGS_TO_ANON_USERS = environment.get('organization-seen-anonymously', False)

LOGIN_REDIRECT_URL = "/projects"
SERVER_EMAIL = "GovReady Q <q@mg.govready.com>"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
NOTIFICATION_FROM_EMAIL_PATTERN = "%s via GovReady Q <q@mg.govready.com>"
NOTIFICATION_REPLY_TO_EMAIL_PATTERN = "%s <q+notification+%d+%s@mg.govready.com>"
NOTIFICATION_REPLY_TO_EMAIL_REGEX = r"q\+notification\+(\d+)\+([a-f\d\-]+)@mg.govready.com"
DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'
NOTIFICATIONS_USE_JSONFIELD = True # allows us to store extra data on Notification instances

GOVREADY_CMS_API_AUTH = environment.get('govready_cms_api_auth')
MAILGUN_API_KEY = environment.get('mailgun_api_key', '') # for the incoming mail route
