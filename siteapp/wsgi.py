import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteapp.settings")
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
if 'runserver' not in sys.argv:
    application = DjangoWhiteNoise(application)
