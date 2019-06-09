from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
import django.contrib.auth.backends
import django.contrib.auth.middleware

import re
from urllib.parse import urlsplit, urlencode

from .models import Organization

allowed_paths = None
account_login_url = None

class ContentSecurityPolicyMiddleware:
    # Set the CSP header on all responses.
    def __init__(self, next_middleware):
        self.next_middleware = next_middleware
    def __call__(self, request):
        # Some of the exceptions that we need:
        # * we embed images from user answers and module static assets using data: URLs in many cases to avoid having to perform many separate requests each needing to re-check authorization
        # * we might be using inline scripts in some of our modules' output documents
        # * we're definitely using inline scripts and CSS throughout our templates, but that could be refactored
        response = self.next_middleware(request)
        response['Content-Security-Policy'] = \
            "default-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response

def QTemplateContextProcessor(request):
    return {
        "APP_VERSION_STRING": settings.APP_VERSION_STRING,
        "APP_VERSION_COMMIT": settings.APP_VERSION_COMMIT,
        "MOUSE_CURSOR_FOLLOWER": getattr(settings, 'MOUSE_CURSOR_FOLLOWER', False),
        "LOGIN_ENABLED": ('django.contrib.auth.backends.ModelBackend' in settings.AUTHENTICATION_BACKENDS),
    }

# This authentication backend is used when Q is behind an enterprise proxy server handling
# authentication. The proxy server passes the username and email address of the authenticated
# user in HTTP headers. Django provides request headers in request.meta["HTTP_HEADER_NAME"]
# format, so we must convert the setting that holds the header name to the way the header
# will appear inside request.meta. We update the user's email address with the one passed
# in the header whenever we come here. But this only occurs when the user is logging in.
# It seems like if the user has an active Django session and the username in the header
# matches the user in the session then the session is kept and ProxyHeaderUserAuthenticationBackend
# is not called.
class ProxyHeaderUserAuthenticationMiddleware(django.contrib.auth.middleware.RemoteUserMiddleware):
    header = "HTTP_" + re.sub(r"[-_]", "_", getattr(settings, 'PROXY_HEADER_AUTHENTICATION_HEADERS', {}).get('username', '').upper())
class ProxyHeaderUserAuthenticationBackend(django.contrib.auth.backends.RemoteUserBackend):
    def authenticate(self, request, remote_user):
        # Let the Django class get the user.
        user = super(ProxyHeaderUserAuthenticationBackend, self).authenticate(request, remote_user)

        if user:
            # Update with the email address provided in an HTTP header.
            email_header = "HTTP_" + re.sub(r"[-_]", "_",settings.PROXY_HEADER_AUTHENTICATION_HEADERS['email'].upper())
            email_addr = request.META.get(email_header)
            if email_addr and user.email != email_addr:
                user.email = email_addr
                user.save()

            # Log.
            import logging
            logger = logging.getLogger(__name__)
            logger.error("login ip={ip} username={username} result={result}".format(
                    ip=request.META.get("REMOTE_ADDR"),
                    username=remote_user,
                    result=("user:%d" % user.id) if user else "fail"
                ))

        # Return.
        return user