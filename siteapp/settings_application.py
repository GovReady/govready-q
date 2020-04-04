# nothing here

import re
from .settings import *

INSTALLED_APPS += [
    #'debug_toolbar',

    'htmlemailer',
    'notifications',
    'dbstorage',
    'guardian',

    'siteapp',
    'guidedmodules',
    'discussion',
    'controls',
    'system_settings',

    'testmocking',
]


if environment.get("trust-user-authentication-headers"):
    # When this is set, the 'username' and 'email' keys hold HTTP header
    # names which control user authentication. Standard authentication
    # is disabled. Instead, user login is handled by a proxy server running
    # in front of Q. These headers are always expected to be set and trusted
    # when this setting is enabled. Per the Django Documentation (https://docs.djangoproject.com/en/dev/howto/auth-remote-user/),
    # you must be sure that your front-end web server does not permit an
    # end-user to submit a spoofed header value for these headers *as well
    # as* other headers that normalize to the same key as seen by Django.
    # Because regular authentication is disabled, before setting this setting
    # you should ensure you'll be able to log in with the proxy using the
    # username of an admin account that is already registered.
    MIDDLEWARE.append('siteapp.middleware.ProxyHeaderUserAuthenticationMiddleware') # must be after AuthenticationMiddleware but before OrganizationSubdomainMiddleware
    AUTHENTICATION_BACKENDS.remove('django.contrib.auth.backends.ModelBackend') # disable the standard login backends
    AUTHENTICATION_BACKENDS.remove('allauth.account.auth_backends.AuthenticationBackend')
    AUTHENTICATION_BACKENDS.append('siteapp.middleware.ProxyHeaderUserAuthenticationBackend') # add backend for this method
    PROXY_HEADER_AUTHENTICATION_HEADERS = environment["trust-user-authentication-headers"]
    print("Trusting authentication headers:", PROXY_HEADER_AUTHENTICATION_HEADERS)
    LOGOUT_REDIRECT_URL = "/sso-logout"
    print("Setting LOGOUT_REDIRECT_URL to", LOGOUT_REDIRECT_URL)

MIDDLEWARE += [
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'siteapp.middleware.ContentSecurityPolicyMiddleware',
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

# Get the version of this software from the VERSION file which has up to two lines.
# The first line is a version string for display. The second line is the git commit
# hash that the build was based on. If the second line isn't present, we use git to
# get the hash of current HEAD, plus a marker if there are local modifications.
with open("VERSION") as f:
    APP_VERSION_STRING = f.readline().strip()
    APP_VERSION_COMMIT = f.readline().strip()
if not APP_VERSION_COMMIT and os.path.exists(".git"):
    import subprocess # nosec
    APP_VERSION_COMMIT = subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"]).strip().decode("ascii")
    if subprocess.run(["/usr/bin/git", "diff-index", "--quiet", "HEAD", "--"]):
        # see https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
        APP_VERSION_COMMIT += "-dirty"
