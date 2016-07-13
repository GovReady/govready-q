# from https://raw.githubusercontent.com/if-then-fund/django-good-settings/master/settings.py

################################################################
# Good defaults for a setttings.py, plus logic for bringing    #
# in settings from various normal places you might store them. #
################################################################

import os, os.path, json

# What's the name of the app containing this file? That determines
# the module for the main URLconf etc. E.g. `govready-q/siteapp/settings.py`
# resolves to 'siteapp'
primary_app = os.path.basename(os.path.dirname(__file__))

# LOAD ENVIRONMENT SETTINGS #
#############################

# shortcut function for getting a file in a 'local' subdirectory
# of the main Django project path (one up for this directory).
def local(fn):
	return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'local', fn)

if os.path.exists(local("environment.json")):
	environment = json.load(open(local("environment.json")))
else:
	# Make some defaults for local development

	# This is how 'manage.py startproject' does it:
	def make_secret_key():
		from django.utils.crypto import get_random_string
		return get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')

	environment = {
		"secret-key": make_secret_key(),
		"debug": True,
		"host": "localhost:8000",
		"https": False,
	}

	print("Create a local/environment.json file! It should contain something like this:")
	print(json.dumps(environment, sort_keys=True, indent=2))

# DJANGO SETTINGS #
###################

# Check environment vars, then the local/environment.json settings
# Required settings
# The SECRET_KEY must be specified in the environment.
SECRET_KEY    = os.getenv('SECRET_KEY', environment["secret-key"])
DEBUG         = os.getenv('DEBUG', environment['debug'])
# Set ALLOWED_HOSTS from the host environment. If it has a port, strip it.
# The port is used in SITE_ROOT_URL must must be removed from ALLOWED_HOSTS.
HOST          = os.getenv('HOST', environment['host'])
ALLOWED_HOSTS = HOST.split(':')[0]
HTTPS         = os.getenv('HTTPS',environment["https"])

## Optional settings either from local/environment.json or env vars
ADMINS        = os.getenv('ADMINS', environment.get("admins", []))
USE_MEMCACHED = os.getenv('USE_MEMCACHED', environment.get('memcached'))
EMAIL         = os.getenv('EMAIL', environment.get('email'))
# STATIC True (as for CF deploys) uses a relative path, STATIC "path"
# uses that path:
STATIC        = os.getenv('STATIC', environment.get('static'))

################ DATABASE SETUP ##############
# Use an Sqlite database at local/db.sqlite, until other database
# settings have been set in the environment.
#
# when DATABASE_URL='mysql2://myuser:mypass@myhost:3306/my_database_name'
# then DATABASES['default'] =
#    {'USER': 'myuser', 'NAME': 'my_database_name', 'HOST': 'myhost', 'PASSWORD': 'mypass', 'PORT': 3306, 'ENGINE': 'django.db.backends.mysql'}
# else DATABASES['default'] =
#    {'ENGINE': 'django.db.backends.sqlite3', 'PASSWORD': None, 'USER': None, 'NAME': 'local/db.sqlite3', 'PORT': None, 'HOST': None}

from urllib.parse import urlparse
url = urlparse(
        os.environ.get(
            'DATABASE_URL',
            'sqlite3:///db.sqlite3'
            )
        )
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql' if 'mysql' in url.scheme else 'django.db.backends.sqlite3',
        'NAME': url.path[1:] if url.scheme == 'mysql2' else local(url.path[1:]),
	    'CONN_MAX_AGE': 60 if url.scheme != 'sqlite3' else None,
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port,
    }
}
print("Using DB: %s", DATABASES['default'])

# Ensure the 'local' directory exists for the default Sqlite
# database.
if 'sqlite3' in DATABASES['default']['NAME']:
	if not os.path.exists(os.path.dirname(local('.'))):
		print("Making local dir for SQLite3 DB")
		os.mkdir(os.path.dirname(local('.')))
################ FINI DATABASE SETUP ##############

# allauth requires the use of the sites framework.
SITE_ID = 1

# Add standard apps to INSTALLED_APPS.
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.staticfiles',
	'django.contrib.sessions',
    'django.contrib.sites', # required by allauth
	'django.contrib.messages',
	'django.contrib.humanize',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # add any allauth social providers as you like
]

# Add test_without_migrations if it is installed. This provides --nomigrations
# to the test management command.
try:
	import test_without_migrations
	INSTALLED_APPS.append('test_without_migrations')
except ImportError:
	pass

# Add standard middleware.
MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]
if DEBUG and os.path.exists(os.path.join(os.path.dirname(__file__), 'helper_middleware.py')):
	MIDDLEWARE_CLASSES.append(primary_app+'.helper_middleware.DumpErrorsToConsole')

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
				'django.core.context_processors.static',
				'django.core.context_processors.tz',
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
AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',
	'allauth.account.auth_backends.AuthenticationBackend', # allauth
	]
ACCOUNT_ADAPTER = primary_app + '.good_settings_helpers.AllauthAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = False # otherwise unconfirmed addresses may block real users
ACCOUNT_DEFAULT_HTTP_PROTOCOL = ("http" if not HTTPS else "https")
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 15 # default of 5 is too low!
ACCOUNT_LOGOUT_ON_GET = True # allow simplified logout link
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PASSWORD_MIN_LENGTH = (4 if DEBUG else 6) # in debugging, allow simple passwords

# improve how the allauth forms are rendered using django-bootstrap forms
from bootstrapform.templatetags.bootstrap import bootstrap#_horizontal
ALLAUTH_FORM_RENDERER = bootstrap#_horizontal


# Setup the cache. The default is a LocMemCache.
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': '127.0.0.1:11211',
	}
}
if USE_MEMCACHED:
	# But if the 'memcached' environment setting is true,
	# enable a memcached cache using the default host/port
	# (see above) *and* enable the cached_db session backend.
	CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
	SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

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

# Dump outbound emails to the console by default for debugging.
# If the "email" environment setting is present, it is a dictionary
# providing an SMTP server to send outbound emails to. TLS is
# always turned on.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[' + HOST + '] '
if EMAIL:
	EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
	EMAIL_HOST = EMAIL["host"]
	EMAIL_PORT = EMAIL["port"]
	EMAIL_HOST_USER = EMAIL["user"]
	EMAIL_HOST_PASSWORD = EMAIL["pw"]
	EMAIL_USE_TLS = True

# If the "https" environment setting is true, set the settings
# that keep sessions and cookies secure.
if HTTPS:
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SECURE = True
	CSRF_COOKIE_HTTPONLY = True
	CSRF_COOKIE_SECURE = True

# Put static files in the virtual path "/static/". When the "static"
# environment setting is set to a string, then it's a local directory path
# where "collectstatic" will put static files. If "static" is simply True, use a
# relative path.
# The ManifestStaticFilesStorage is activated.
STATIC_URL = '/static/'
if STATIC in ['True', 'true', True]:
	PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
	STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
	STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
elif STATIC:
	STATIC_ROOT = STATIC
	STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Add a convenience setting "SITE_ROOT_URL" that stores the root URL
# of the website, constructed from the "https" and "host" environment
# settings
SITE_ROOT_URL = "%s://%s" % (("http" if not HTTPS else "https"), HOST)

# Load all additional settings from settings_application.py.
from .settings_application import *
