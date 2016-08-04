from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse

from urllib.parse import urlsplit, urlencode

from .models import Organization

class OrganizationSubdomainMiddleware:
    def process_request(self, request):
        # Use a different set of routes depending on whether the request
        # is for q.govready.com, the special landing domain, or an
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

        # Is this a request for our main landing domain?
        if request_host == main_landing_domain:
            # This is one of our recognized main domain names. We serve
            # a special set of URLs for our main domain landing pages.
            request.urlconf = 'siteapp.urls_landing'
            return None # continue with normal request processing

        # Is this a request for an organization subdomain?
        if request_host.endswith('.' + settings.ORGANIZATION_PARENT_DOMAIN):
            subdomain = request_host[:-len(settings.ORGANIZATION_PARENT_DOMAIN)-1]

            # Does this subdomain correspond with a known organization?
            org = Organization.objects.filter(subdomain=subdomain).first()
            if org:
                # Only authenticated users can see inside organizational subdomains.
                # We don't want to reveal any information about the organization.
                # Except:
                # * the log in and sign up pages must be accessible anonymously.
                # * the invitation acceptance URL must be accessible while logged in
                #   but not yet a member of the organization
                if request.path.startswith("/invitation/accept/"):
                    # Allow this through.
                    request.organization = org
                    return None

                elif request.user.is_authenticated() and org.can_read(request.user):
                    # Ok, this request is good.

                    # Set the Organiation on the request object.
                    request.organization = org

                    # Pre-load the user's settings task if the user is logged in,
                    # so that we have global access to it.
                    request.user.localize_to_org(request.organization)

                    # Continue with normal request processing.
                    return None

        # The HTTP host did not match a domain we can serve or that the user is authenticated
        # to see.

        # Log the user out if they don't have permission to see this subdomain.
        # Otherwise the login page redirects to the home page, and then we
        # get back here and redirect to the login page, infinitely.
        if request.user.is_authenticated():
            from django.contrib.auth import logout
            from django.contrib import messages
            logout(request)
            messages.add_message(request, messages.ERROR, 'You are not a member of this organization.')

        # The user isn't authenticated to see inside the organization subdomain, but
        # we have to allow them to log in or sign up.
        allowed_paths = [reverse("account_login"), reverse("account_signup")]
        if request.path in allowed_paths:
            # Don't leak any organization information. But do render the login/signup
            # pages and allow the routes for the form POSTs from there.
            return None

        # The user is not authenticated on this domain, is logged out, and is requesting
        # a path besides login/signup. Redirect to the login route.
        return HttpResponseRedirect(allowed_paths[0] + "?" + urlencode({ "next": request.path }))
