# nothing here

from .settings import *

INSTALLED_APPS += [
    'bootstrapform',
    'htmlemailer',

    'siteapp',
    'guidedmodules',
    'discussion',
]

SERVER_EMAIL = "GovReady Q <q@mg.govready.com>"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
