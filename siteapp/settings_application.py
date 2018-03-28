# nothing here

import re
from .settings import *

INSTALLED_APPS += [
    #'debug_toolbar',

    'htmlemailer',
    'notifications',
    'dbstorage',

    'siteapp',
    'guidedmodules',
    'discussion',
]

MIDDLEWARE += [
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'siteapp.middleware.OrganizationSubdomainMiddleware',
    'guidedmodules.middleware.InstrumentQuestionPageLoadTimes',
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'siteapp.middleware.QTemplateContextProcessor',
]

AUTHENTICATION_BACKENDS += ['siteapp.models.DirectLoginBackend']

INTERNAL_IPS = ['127.0.0.1'] # for django_debug_toolbar

# Allow run-time disabling of the Django Debug Toolbar.
DISABLE_DJANGO_DEBUG_TOOLBAR = False
def DEBUG_TOOLBAR_SHOW_TOOLBAR_CALLBACK(r):
    import debug_toolbar.middleware
    return debug_toolbar.middleware.show_toolbar(r) and not DISABLE_DJANGO_DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': DEBUG_TOOLBAR_SHOW_TOOLBAR_CALLBACK,
}

# ALLWOED_HOSTS is set based on environment['host'], which gives us
# our landing page domain. Also allow all subdomains of the organization
# parent domain.
LANDING_DOMAIN = environment["host"]
ORGANIZATION_PARENT_DOMAIN = environment.get('organization-parent-domain', 'localhost')
ALLOWED_HOSTS += ['.' + ORGANIZATION_PARENT_DOMAIN]
SINGLE_ORGANIZATION_KEY = environment.get('single-organization')
REVEAL_ORGS_TO_ANON_USERS = (SINGLE_ORGANIZATION_KEY is not None) or environment.get('organization-seen-anonymously', False)

LOGIN_REDIRECT_URL = "/projects"
EMAIL_DOMAIN = environment.get("email", {}).get("domain", environment["host"].split(":")[0])
SERVER_EMAIL = ("GovReady Q <q@%s>" % EMAIL_DOMAIN)
DEFAULT_FROM_EMAIL = SERVER_EMAIL
NOTIFICATION_FROM_EMAIL_PATTERN = "%s via GovReady Q <q@" + EMAIL_DOMAIN + ">"
NOTIFICATION_REPLY_TO_EMAIL_PATTERN = "%s <q+notification+%d+%s@" + EMAIL_DOMAIN + ">"
NOTIFICATION_REPLY_TO_EMAIL_REGEX = r"q\+notification\+(\d+)\+([a-f\d\-]+)@" + re.escape(EMAIL_DOMAIN) + ""
DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'
NOTIFICATIONS_USE_JSONFIELD = True # allows us to store extra data on Notification instances

GOVREADY_CMS_API_AUTH = environment.get('govready_cms_api_auth')
MAILGUN_API_KEY = environment.get('mailgun_api_key', '') # for the incoming mail route

VALIDATE_EMAIL_DELIVERABILITY = True
 
# Get the version of this software.
import os.path
if os.path.exists("VERSION"):
    # Get the version from the VERSION file which has two lines.
    # The first line is a version string for display. The second
    # line is the git commit hash that the build was based on.
    with open("VERSION") as f:
        APP_VERSION_STRING = f.readline().strip()
        APP_VERSION_COMMIT = f.readline().strip()
else:
    # If there is no VERSION file, query the git working directory.
    import subprocess # nosec
    APP_VERSION_STRING = subprocess.check_output(["/usr/bin/git", "describe", "--tags", "--always"]).strip().decode("ascii")
    APP_VERSION_COMMIT = subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"]).strip().decode("ascii")

