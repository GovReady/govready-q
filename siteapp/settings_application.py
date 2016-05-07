# nothing here

from .settings import *

INSTALLED_APPS += [
    'bootstrapform',
    'htmlemailer',

    'siteapp',
    'guidedmodules',
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'siteapp.betteruser.DirectLoginBackend']
VALIDATE_EMAIL_DELIVERABILITY = True
