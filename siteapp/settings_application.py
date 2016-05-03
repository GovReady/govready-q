# nothing here

from .settings import *

INSTALLED_APPS += [
    'django.contrib.sites',
    'account',
    'pinax_theme_bootstrap',
    'bootstrapform',
    'htmlemailer',

    'siteapp',
    'guidedmodules',
]

# For pinax (account, pinax_theme_bootstrap):
TEMPLATES[0]['OPTIONS']['context_processors'].extend([
	"account.context_processors.account",
	"pinax_theme_bootstrap.context_processors.theme"])
MIDDLEWARE_CLASSES += [
    "account.middleware.LocaleMiddleware",
    "account.middleware.TimezoneMiddleware",
]
SITE_ID = 1

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'siteapp.views.DirectLoginBackend']
