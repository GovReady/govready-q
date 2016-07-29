# nothing here

from .settings import *

INSTALLED_APPS += [
    'bootstrapform',
    'htmlemailer',
    'notifications',

    'siteapp',
    'guidedmodules',
    'discussion',
]

MIDDLEWARE_CLASSES += [
	'siteapp.middleware.OrganizationSubdomainMiddleware',
]

AUTHENTICATION_BACKENDS += ['siteapp.models.DirectLoginBackend']

SERVER_EMAIL = "GovReady Q <q@mg.govready.com>"
DEFAULT_FROM_EMAIL = SERVER_EMAIL

MODULES_PATH = environment.get('modules-path', 'modules')

GOVREADY_CMS_API_AUTH = environment.get('govready_cms_api_auth')
