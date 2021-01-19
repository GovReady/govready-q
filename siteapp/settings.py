# from https://raw.githubusercontent.com/if-then-fund/django-good-settings/master/settings.py

################################################################
# Good defaults for a settings.py, plus logic for bringing    #
# in settings from various normal places you might store them. #
################################################################

import os, os.path, json
from platform import uname, system
from django.core.exceptions import ValidationError
# What's the name of the app containing this file? That determines
# the module for the main URLconf etc.
primary_app = os.path.basename(os.path.dirname(__file__))

# LOAD ENVIRONMENT SETTINGS #
#############################

# shortcut function for getting a file in a 'local' subdirectory
# of the main Django project path (one up for this directory).
def local(fn):
	return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'local', fn)

# This is how 'manage.py startproject' does it:
def make_secret_key():
	from django.utils.crypto import get_random_string
	return get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')

# Gather parameter settings from 'local/environment.json' file
# NOTE: `environment` here refers to locally created environment data object and not OS level environment variables
if os.path.exists(local("environment.json")):
        try:
                environment = json.load(open(local("environment.json")))
        except json.decoder.JSONDecodeError as e:
                print("%s is not in JSON format" % local("environment.json"))
                print(open(local("environment.json")).read())
                exit(1)
else:
	# Make some defaults and show the user.
	environment = {
		"secret-key": make_secret_key(),
		"debug": True,
		"https": False,
		"host": "localhost:8000",
	}

	# Show the defaults.
	print("\nCouldn't find `local/environment.json` file. Generating default environment params.")
	print("Please create a '%s' file containing something like this:" % local("environment.json"))
	environment["secret-key"] = make_secret_key() # Generate a new key since the initial one was printed for the user for edification
	print(json.dumps(environment, sort_keys=True, indent=2))

# Load pre-specified admin users
# Example: "govready_admins":[{"username": "username", "email":"first.last@example.com", "password": "REPLACEME"}]
GOVREADY_ADMINS = environment.get("govready_admins") or []

# DJANGO SETTINGS #
###################

# The SECRET_KEY should be specified in the environment file, otherwise generate a fresh one on each run.
SECRET_KEY = environment.get("secret-key") or make_secret_key()

# The DEBUG flag must be set in the environment.
DEBUG = bool(environment.get("debug"))
ADMINS = environment.get("admins") or []

# Set GOVREADY_URL if 'govready-url' set in environment.json.
from urllib.parse import urlparse
GOVREADY_URL = urlparse(environment.get("govready-url",""))

# Set Django's ALLOWED_HOSTS parameter.
# Use the deprecated 'host' environment parameter and preferred 'govready-url'.
# The port is used in SITE_ROOT_URL must be removed from ALLOWED_HOSTS.
ALLOWED_HOSTS = []
if "host" in environment:
	ALLOWED_HOSTS = [environment["host"].split(':')[0]]
	print("WARNING: Use of 'host' environment parameter deprecated. Please use 'govready-url' environment parameter in future.")
if (GOVREADY_URL.hostname and GOVREADY_URL.hostname != "") and (GOVREADY_URL.hostname not in ALLOWED_HOSTS):
	ALLOWED_HOSTS.append(GOVREADY_URL.hostname)
print("INFO: ALLOWED_HOSTS", ALLOWED_HOSTS)
# Support multiple hosts if set
# `allowed_hosts` must be an ARRAY
if "allowed_hosts" in environment:
	ALLOWED_HOSTS.extend(environment["allowed_hosts"])

# allauth requires the use of the sites framework.
SITE_ID = 1

# Add standard apps to INSTALLED_APPS.
DJANGO_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.staticfiles',
	'django.contrib.sessions',
	'django.contrib.sites', # required by allauth
	'django.contrib.messages',
	'django.contrib.humanize',

]
THIRD_PARTY_APPS = [
	'bootstrap3',
	'allauth',
	'allauth.account',
	'allauth.socialaccount',
	'simple_history',
	# add any allauth social providers as you like
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS

# Add test_without_migrations if it is installed. This provides --nomigrations
# to the test management command.
try:
	import test_without_migrations
	INSTALLED_APPS.append('test_without_migrations')
except ImportError:
	print("WARNING: 'test_without_migrations' could not be imported")


# profile every request and save the HTML output to the folder profiles
if DEBUG:
	PYINSTRUMENT_PROFILE_DIR = 'profiles'

# Add standard middleware.
MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'simple_history.middleware.HistoryRequestMiddleware',
	'pyinstrument.middleware.ProfilerMiddleware',
]
if environment["debug"] and os.path.exists(os.path.join(os.path.dirname(__file__), 'helper_middleware.py')):
	MIDDLEWARE.append(primary_app+'.helper_middleware.DumpErrorsToConsole')

# Load templates for app directories and from a main `templates` directory located
# at the project root. Add standard context processors.
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')],
		'OPTIONS': {
			'debug': DEBUG,
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'django.template.context_processors.request', # allauth
			],
			'loaders': [
					'django.template.loaders.filesystem.Loader',
					'django.template.loaders.app_directories.Loader',
				],
		},
	},
]

# When in production, cache the templates once loaded from disk.
if not DEBUG:
	# Wrap the template loaders in the cached loader.
	TEMPLATES[0]['OPTIONS']['loaders'] = [
		('django.template.loaders.cached.Loader', TEMPLATES[0]['OPTIONS']['loaders'])
	]

# Authentication. Use the User model in the primary
# app, so that you can attach profile information to it.
# Use 'allauth', configured to have users log in by
# username. The email login is broken, like most Django
# methods, because it allows someone to take over an
# email address before confirming ownership.
AUTH_USER_MODEL = primary_app + '.User'
LOGIN_REDIRECT_URL = "/"
AUTHENTICATION_BACKENDS = [ # see settings_application.py for how this is possible changed later
	'django.contrib.auth.backends.ModelBackend',
	'allauth.account.auth_backends.AuthenticationBackend', # allauth
	'guardian.backends.ObjectPermissionBackend',
	]

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
if (GOVREADY_URL.scheme == "https") or (GOVREADY_URL.scheme == "" and "https" in environment and environment["https"]):
	ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
if "https" in environment:
	print("WARNING: Use of 'https' environment paramenter deprecated. Please use 'govready-url' environment parameter in future.")

ACCOUNT_ADAPTER = primary_app + '.good_settings_helpers.AllauthAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = False # otherwise unconfirmed addresses may block real users
ACCOUNT_EMAIL_REQUIRED = True # otherwise pwd resets are not possible
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 15 # default of 5 is too low!
ACCOUNT_LOGOUT_ON_GET = True # allow simplified logout link
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PASSWORD_MIN_LENGTH = (4 if DEBUG else 6) # in debugging, allow simple pwds

# improve how the allauth forms are rendered using django-bootstrap forms,
# in combination with a monkeypatch run elsewhere
import bootstrap3.templatetags.bootstrap3
ALLAUTH_FORM_RENDERER = bootstrap3.templatetags.bootstrap3.bootstrap_form

# Require strong passwords (but not when debugging because that's annoying).
if not DEBUG:
	AUTH_PASSWORD_VALIDATORS = [
		{
			'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
		},
		{
			'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
			'OPTIONS': {
				'min_length': 9,
			}
		},
		{
			'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
		},
		{
			'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
		},
	]

# Use an Sqlite database at local/db.sqlite, until other database
# settings have been set in the environment.
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': local('db.sqlite3'),
		'CONN_MAX_AGE': 60*5, # 5 min
	}
}
if not environment.get('db'):
	# Ensure the 'local' directory exists for the default Sqlite
	# database and then try touching the path to check for write
	# access. If Sqlite can't open the database for reading, it
	# gives an unhelpful error, so we issue our own error. If
	# we create an empty file, Sqlite is fine with that.
	if not os.path.exists(os.path.dirname(local('.'))):
		os.mkdir(os.path.dirname(local('.')))
	with open(DATABASES['default']['NAME'], 'a') as f:
		pass

elif isinstance(environment['db'], str):
	# Set up the database using a connection string.
	import dj_database_url
	DATABASES['default'] = dj_database_url.parse(environment['db'], conn_max_age=600)
else:
	# Enable database connection pooling (unless overridden in the
	# environment settings).
	DATABASES['default']['CONN_MAX_AGE'] = 60
	DATABASES['default'].update(environment['db'])

# Setup the cache. The default is a LocMemCache.
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': '127.0.0.1:11211',
	}
}
if environment.get('memcached'):
	# But if the 'memcached' environment setting is true,
	# enable a memcached cache using the default host/port
	# (see above) *and* enable the cached_db session backend.
	CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
	SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Logging.
# Django disables console logging when DEBUG is false but console logging
# is handy, especially in simple Docker deployments. Unhandled exception
# stack traces are logged to the console.
from django.utils.log import DEFAULT_LOGGING
LOGGING = DEFAULT_LOGGING
if not DEBUG:
	LOGGING['handlers']['console']['filters'].remove('require_debug_true')
	LOGGING['handlers']['console']['level'] = 'WARNING'
if environment.get("syslog"):
	# install the rfc5424-logging-handler package. Add a top-level
	# logger that sends everything to the syslog receiver.
	import socket
	hostname, port = environment["syslog"].split(":", 1)
	LOGGING['formatters'].update({
		'syslog': {
			'format': '%(levelname)s %(message)s',
			'datefmt': '%Y-%m-%dT%H:%M:%S',
		},
	})
	LOGGING['handlers'].update({
		'syslog': {
			'level': 'WARNING',
			'class': 'rfc5424logging.handler.Rfc5424SysLogHandler',
			'address': (hostname, int(port)),
			'socktype': socket.SOCK_STREAM,
			'formatter': 'syslog',
			'hostname': environment['host'] + "@" + socket.gethostname()
		}
	})
	LOGGING['loggers'][''] = {
		'handlers': ['syslog'],
		'level': 'INFO',
	}

SILENCED_SYSTEM_CHECKS = []
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
# Settings that have normal values based on the primary app
# (the app this file resides in).

ROOT_URLCONF = primary_app + '.urls'
WSGI_APPLICATION = primary_app + '.wsgi.application'

# Turn on TZ-aware datetimes. Store times in UTC in the database.

TIME_ZONE = 'UTC'
USE_TZ = True

# Use localization but not internationalization. You probably will
# want to change these if you are not making a U.S.-focused website.

LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = True

# This might be redundant, but if we're using locale directly we
# need to set this on startup.

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Dump outbound emails to the console by default for debugging.
# If the "email" environment setting is present, it is a dictionary
# providing an SMTP server to send outbound emails to. TLS is
# always turned on.

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
if (GOVREADY_URL.hostname and GOVREADY_URL.hostname != ""):
	EMAIL_SUBJECT_PREFIX = '[' + GOVREADY_URL.hostname + '] '
elif "host" in environment:
	EMAIL_SUBJECT_PREFIX = '[' + environment['host'] + '] '
else:
	EMAIL_SUBJECT_PREFIX = '[' + 'localhost' + '] '
	print("WARNING: host not properly defined to set EMAIL_SUBJECT_PREFIX")

if environment.get("email", {}).get("host"):
	EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
	EMAIL_HOST = environment["email"]["host"]
	EMAIL_PORT = environment["email"]["port"]
	EMAIL_HOST_USER = environment["email"]["user"]
	EMAIL_HOST_PASSWORD = environment["email"]["pw"]
	EMAIL_USE_TLS = True

# If the deprecated "https" environment setting is true or preferred 'govready-url' includes "https",
# set the settings that keep sessions and cookies secure and redirect any non-HTTPS
# requests to HTTPS.
# Give GOVREADY_URL.scheme from 'govready-url' precedence.

if (GOVREADY_URL.scheme == "https") or (GOVREADY_URL.scheme == "" and "https" in environment and environment["https"]):
	print("INFO: Connection scheme is 'https'.")
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SECURE = True
	CSRF_COOKIE_HTTPONLY = True
	CSRF_COOKIE_SECURE = True
	SECURE_HSTS_SECONDS = 31536000
	SECURE_HSTS_INCLUDE_SUBDOMAINS = True
	if environment.get("secure_ssl_redirect", False):
		# Force Django to redirect non-secure SSL connections to secure SSL connections
		# NOTE: Setting to True while simultaneously using a http proxy like NGINX
		#       that is also redirecting can lead to infinite redirects.
		#       See: https://docs.djangoproject.com/en/3.0/ref/settings/#secure-ssl-redirect
		#       SECURE_SSL_REDIRECT is False by default.
		SECURE_SSL_REDIRECT = True
		print("INFO: SECURE_SSL_REDIRECT is set to 'True'. May cause infinite redirects behind reverse proxies.")
else:
	print("INFO: Connection scheme is 'http'.")
	# Silence some checks about HTTPS.
	SILENCED_SYSTEM_CHECKS += [
		'security.W004', # SECURE_HSTS_SECONDS not set
		'security.W008', # SECURE_SSL_REDIRECT not set
		'security.W012', # SESSION_COOKIE_SECURE not set
		'security.W016', # CSRF_COOKIE_SECURE not set
	]

# Other security headers.
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY' # don't allow site to be embedded in iframes

# Put static files in the virtual path "/static/". When the "static"
# environment setting is present, then it's a local directory path
# where "collectstatic" will put static files.
#
# Uncollected static files that ship with GovReady are located in `siteapp/static`.
# In development (e.g. debug = true), Django will *ignore* the STATIC_ROOT setting and
# search installed application paths when resolving STATIC_URL to find actual files.
#
# In production (e.g. debug = false), Django will use the STATIC_ROOT setting
# when resolving STATIC_URL to find the path to actual files.
# Also, the `manage.py collectstatic` will copy found static files into the
# STATIC_ROOT path.
#
# A duplication of files can occur in production deployments when SITE_ROOT
# is defined as `siteapp/static`. Collectstatic does post-processing on files and 
# appends a hash and then builds a manifest for static files. As `collectstatic` command
# repeatedly is run, the result is reading and aggregating static files from and into
# the same directory. This will eventually cause an errors as file names grow too long
# and the static file manifest and actual file names break.
#
# The ManifestStaticFilesStorage is activated, too, for alternaye storing/serving of static assets.
#
uncollected_static_files = "siteapp/static"
STATIC_URL = '/static/'
STATIC_ROOT = 'static_root/'
if environment.get("static"):
	STATIC_ROOT = environment["static"]
	STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# Check to make sure STATIC_ROOT is not `siteapp/static`
siteapp_path = os.getcwd()
if os.path.join(siteapp_path, STATIC_ROOT) == os.path.join(siteapp_path, "siteapp/static"):
	raise ValidationError('STATIC_ROOT directory for collecting static files should never be set to source of uncollected static files (e.g. `siteapp/static`). Please fix environment `static` setting.')

# Add a convenience setting "SITE_ROOT_URL" that stores the root URL of the website.
# Construct value from preferred "govready-url" environment parameter and temporarily
# support the deprecated "https" and "host" environment settings.
SITE_ROOT_URL = None
if (GOVREADY_URL.hostname and GOVREADY_URL.hostname != ""):
	SITE_ROOT_URL = "{}://{}".format(GOVREADY_URL.scheme, GOVREADY_URL.netloc)
	print("INFO: 'SITE_ROOT_URL' set to {} ".format(SITE_ROOT_URL))
elif "host" in environment and "https" in environment:
	SITE_ROOT_URL = "%s://%s" % (("http" if not environment["https"] else "https"), environment["host"])
	print("INFO: 'SITE_ROOT_URL' set to {} ".format(SITE_ROOT_URL))
else:
	print("CRITICAL: No parameters set to determine SITE_ROOT_URL.")

# Enable custom branding. If "branding" is set, it's the name of an
# app to add and whose templates supersede the built-in templates.
if environment.get("branding"):
	INSTALLED_APPS.append(environment["branding"])
	TEMPLATES[0].setdefault('DIRS', [])\
		.insert(0, os.path.join(environment["branding"], 'templates'))

HEADLESS = False if environment.get("test_visible") else True
DOS = True if system() == "Windows" or 'Microsoft' in uname().release else False
# Load all additional settings from settings_application.py.
from .settings_application import *

# Load logging configuration from settings_logging.py.
from .settings_logging import *
