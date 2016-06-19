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

AUTHENTICATION_BACKENDS += ['siteapp.models.DirectLoginBackend']

SERVER_EMAIL = "GovReady Q <q@mg.govready.com>"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
