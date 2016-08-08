import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteapp.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
if os.getenv('VCAP_APPLICATION'):
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(application)
