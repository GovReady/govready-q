import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteapp.settings")
from django.core.wsgi import get_wsgi_application

django_application = get_wsgi_application()

# WSGI redirect logic from
# https://github.com/GrahamDumpleton/mod_wsgi/issues/86
def application_redirect(environ, start_response, http_host):
    headers = []
    headers.append(('Location', 'https://%s%s%s' % (
            http_host, environ.get('SCRIPT_NAME'),
            environ.get('PATH_INFO'))))
    start_response('302 OK', headers)
    yield ''

def application(environ, start_response):
    http_host = environ.get('HTTP_HOST')

    # When running inside a Cloud Foundry container, we may get HTTP
    # requests which we will redirect to HTTPS. TODO: Handle this at
    # the infrastructure level?
    if (environ.get('wsgi.url_scheme', 'http') != 'https') and os.getenv('VCAP_APPLICATION'):
        return application_redirect(environ, start_response, http_host)

    return django_application(environ, start_response)
