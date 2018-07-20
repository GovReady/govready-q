from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

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
        # * we load some media, like the user's profile picture in the header, from a URL at the landing domain even if the user is on an organization domain
        # * we embed images from user answers and module static assets using data: URLs in many cases to avoid having to perform many separate requests each needing to re-check authorization
        # * we might be using inline scripts in some of our modules' output documents
        # * we're definitely using inline scripts and CSS throughout our templates, but that could be refactored
        response = self.next_middleware(request)
        response['Content-Security-Policy'] = \
            "default-src 'self' data: {}; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'".format(
                settings.LANDING_DOMAIN
            )
        return response

class OrganizationSubdomainMiddleware:
    def __init__(self, next_middleware):
        self.next_middleware = next_middleware

    def __call__(self, request):
        # If the user is on an organization subdomain but is not logged in and authorized,
        # then we redirect to the login page on that subdomain.
        #
        # Also if the user is on 127.0.0.1 for testing, we redirect to 'localhost'.
        response = self.check_subdomain(request)
        if response is not None:
            return response

        # Otherwise, the user is permitted to view a page on this subdomain.
        return self.next_middleware(request)

    def process_exception(self, request, exception):
        print("Error processing", request, ":", exception)

    def check_subdomain(self, request):
        global allowed_paths
        global account_login_url

        # Use a different set of routes depending on whether the request
        # is for q.govready.com (the special landing domain) or an
        # organization subdomain.

        # Get the hostname in the UA's original HTTP request. It may be
        # a HOST:PORT --- just take the HOST portion.
        request_host = request.get_host().split(":")[0]

        # When debugging, the Django runserver server uses this host.
        # But we can't do subdomains on that hostname. As a convenience,
        # redirect to "localhost".
        if settings.DEBUG and request_host == "127.0.0.1":
            return HttpResponseRedirect("http://localhost:" + request.get_port() + request.path)

        # What is our main landing domain?
        s = urlsplit(settings.SITE_ROOT_URL)
        main_landing_domain = s[1].split(":")[0]

        # Is this a request for our main landing domain? The main landing domain is not
        # used when the "single-organization" mode is used.
        if request_host == main_landing_domain and not settings.SINGLE_ORGANIZATION_KEY:
            # This is one of our recognized main domain names. We serve
            # a special set of URLs for our main domain landing pages.
            request.urlconf = 'siteapp.urls_landing'
            return None # continue with normal request processing

        elif request.path.startswith("/api/") and settings.SINGLE_ORGANIZATION_KEY:
            # This is an API interaction. In multi-org configurations, the API
            # is served from the landing domain (and would be handled by this blocks
            # first if conditional). In single-org configurations the URLconfs are 
            # merged, that is OK becasue we then check the user 
            # auth on even the landing pages. We have to skip that because API
            # auth is handled by the view.
            return None # continue with normal request processing

        # Is this a request for an organization subdomain?
        elif request_host.endswith('.' + settings.ORGANIZATION_PARENT_DOMAIN) or settings.SINGLE_ORGANIZATION_KEY:
            if not settings.SINGLE_ORGANIZATION_KEY:
                # Get the subdomain from the request host.
                subdomain = request_host[:-len(settings.ORGANIZATION_PARENT_DOMAIN)-1]
            else:
                # The subdomain is fixed as the value of the setting.
                subdomain = settings.SINGLE_ORGANIZATION_KEY

            # Does this subdomain correspond with a known organization?
            org = Organization.objects.filter(subdomain=subdomain).first()
            if org:
                request.unauthenticated_organization_subdomain = org
                if request.user.is_authenticated and org.can_read(request.user):
                    # This request is from an authenticated user who is
                    # authorized to participate in the organization.

                    # Set the Organiation on the request object.
                    request.organization = org

                    # Pre-load the user's settings task if the user is logged in,
                    # so that we have global access to it.
                    request.user.localize_to_org(request.organization)

                    # Continue with normal request processing.
                    return None

                # The user isn't a participant in the organization but we may
                # still reveal which org this is if...

                # The invitation acceptance URL must be accessible while logged in
                # but not yet a member of the organization.
                elif request.path.startswith("/invitation/accept/"):
                    # Allow this through, revealing which org this is.
                    request.organization = org
                    return None

        # The HTTP host did not match a domain we can serve.
        else:
            from django.core.exceptions import DisallowedHost
            import json
            parent_domain = ".".join(request_host.split(".")[1:]) or "<not applicable, domain has no parent>"
            raise DisallowedHost(
                ("You've requested a page at %s but this instance has been configured to only serve pages at '%s' and '*.%s'. "
                    + "To serve pages on this domain, edit your local/environment.json and set the 'host' key to %s or set the 'organization-parent-domain' "
                    + "key to %s.")
                    % (request_host,
                       main_landing_domain, settings.ORGANIZATION_PARENT_DOMAIN,
                       json.dumps(request.get_host()), json.dumps(parent_domain)))

        # The user is not authenticated to see the organization subdomain page they requested.

        # Log the user out. Otherwise the login page redirects to the home page, and then we
        # get back here and redirect to the login page, infinitely.
        if request.user.is_authenticated:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("invalidorg subdomain={subdomain} ip={ip} username={username}".format(
                subdomain=subdomain,
                ip=request.META.get("REMOTE_ADDR"),
                username=request.POST.get("username")
            ))

            from django.contrib.auth import logout
            from django.contrib import messages
            logout(request)
            messages.add_message(request, messages.ERROR, 'You are not a member of this organization.')

        # The user isn't authenticated to see inside the organization subdomain, but
        # we have to allow them to log in, sign up, and reset their password (both
        # submitting the form and then hitting the email confirmation link). Build
        # a white list of allowed URL patterns by reversing the known URL names
        # from allauth/account/urls.py. Because account_reset_password_from_key has
        # URL parameters, turn the reverse'd URLs into regular expressions to match
        # against.
        if allowed_paths == None:
            import re
            allowed_paths = [
                reverse("homepage"),
                reverse("account_login"), reverse("account_signup"),
                reverse("account_reset_password"), reverse("account_reset_password_done"), reverse("account_reset_password_from_key", kwargs={"uidb36":"aaaaaaaa", "key":"aaaaaaaa"}), reverse("account_reset_password_from_key_done")]
            allowed_paths = re.compile("|".join(("^" + re.escape(path).replace("aaaaaaaa", ".+") + "$") for path in allowed_paths))

        if allowed_paths.match(request.path):
            # Don't leak any organization information, unless this deployment
            # allows leaking on login pages.
            if org and settings.REVEAL_ORGS_TO_ANON_USERS:
                request.organization = org

            # Render the page --- including the POST routes.
            return None

        # Do the reverse once.
        if account_login_url is None:
            account_login_url = reverse("homepage")

        # The user is not authenticated on this domain, is logged out, and is requesting
        # a path besides login/signup. Redirect to the login route.
        qs = ""
        if request.path not in (account_login_url, settings.LOGIN_REDIRECT_URL):
            qs = "?" + urlencode({ "next": request.path })
        return HttpResponseRedirect(account_login_url + qs)

def QTemplateContextProcessor(request):
    return {
        "APP_VERSION_STRING": settings.APP_VERSION_STRING,
        "APP_VERSION_COMMIT": settings.APP_VERSION_COMMIT,
        "MOUSE_CURSOR_FOLLOWER": getattr(settings, 'MOUSE_CURSOR_FOLLOWER', False),
    }