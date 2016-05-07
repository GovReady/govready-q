# from https://raw.githubusercontent.com/if-then-fund/django-good-settings/master/settings.py

################################################################
# Good defaults for a setttings.py, plus logic for bringing    #
# in settings from various normal places you might store them. #
################################################################

import os, os.path, json

# What's the name of the app containing this file? That determines
# the module for the main URLconf etc.
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
	# Make some defaults.

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

SECRET_KEY = environment["secret-key"]
DEBUG = environment["debug"]

# Set ALLOWED_HOSTS from the host environment. If it has a port, strip it.
ALLOWED_HOSTS = [environment["host"].split(':')[0]]

# Applications & middleware

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.staticfiles',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.humanize',
]

# Add test_without_migrations if it is installed. This provides --nomigrations
# to the test management command.
try:
	import test_without_migrations
	INSTALLED_APPS.append('test_without_migrations')
except ImportError:
	pass

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
if environment["debug"] and os.path.exists(os.path.join(os.path.dirname(__file__), 'helper_middleware.py')):
	MIDDLEWARE_CLASSES.append(primary_app+'.helper_middleware.DumpErrorsToConsole')

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
			],
			'loaders': [
					'django.template.loaders.filesystem.Loader',
					'django.template.loaders.app_directories.Loader',
				],
		},
	},
]
if not DEBUG:
	# Wrap the template loaders in the cached loader.
	TEMPLATES[0]['OPTIONS'][loaders] = [
		('django.template.loaders.cached.Loader', TEMPLATES[0]['OPTIONS'][loaders])
	]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# Database and Cache

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': local('db.sqlite3'),
	}
}
if not environment.get('db'):
	if not os.path.exists(os.path.dirname(local('.'))):
		os.mkdir(os.path.dirname(local('.')))
else:
	DATABASES['default']['CONN_MAX_AGE'] = 60
	DATABASES['default'].update(environment['db'])

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': '127.0.0.1:11211',
	}
}
if environment.get('memcached'):
	CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
	SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Settings

ROOT_URLCONF = primary_app + '.urls'
WSGI_APPLICATION = primary_app + '.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = True
USE_TZ = True

AUTH_USER_MODEL = primary_app + '.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[' + environment['host'] + '] '

if environment.get("email"):
	EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
	EMAIL_HOST = environment["email"]["host"]
	EMAIL_PORT = environment["email"]["port"]
	EMAIL_HOST_USER = environment["email"]["user"]
	EMAIL_HOST_PASSWORD = environment["email"]["pw"]
	EMAIL_USE_TLS = True

if environment["https"]:
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SECURE = True
	CSRF_COOKIE_HTTPONLY = True
	CSRF_COOKIE_SECURE = True

# Paths

STATIC_URL = '/static/'
if environment.get("static"):
	STATIC_ROOT = environment["static"]
	STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
LOGIN_URL = '/registration/login/'
LOGIN_REDIRECT_URL = '/'

# Convenience.

SITE_ROOT_URL = "%s://%s" % (("http" if not environment["https"] else "https"), environment["host"])

# Load all additional settings from settings_application.py.
from .settings_application import *
