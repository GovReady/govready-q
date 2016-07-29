from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse

from urllib.parse import urlencode

from .models import Organization

class OrganizationSubdomainMiddleware:
    def process_request(self, request):
        # Use a different set of routes depending on whether the request
        # is for q.govready.com, the special landing domain, or an
        # organization subdomain.

        # Get the hostname in the UA's original HTTP request. It may be
        # a HOST:PORT.
        request_host = request.get_host().split(":")[0]

        for top_domain in settings.ALLOWED_HOSTS:
            # The ALLOWED_HOSTS domain might start with a '.' to indicate
            # it allows all subdomains. Strip that off.
            top_domain = top_domain.lstrip('.')

            if request_host == top_domain:
                # This is one of our recognized main domain names. We serve
                # a special set of URLs for our main domain landing pages.
                request.urlconf = 'siteapp.urls_landing'
                return None # continue with normal request processing

            elif request_host.endswith("." + top_domain):
                # This is a subdomain.
                subdomain = request_host[:-len(top_domain)-1]

                # Does this subdomain correspond with a known organization?
                org = Organization.objects.filter(subdomain=subdomain).first()
                if not org:
                    continue

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

                elif not request.user.is_authenticated() or not org.can_read(request.user):
                    # Log the user out if they don't have permission to see this subdomain.
                    # Otherwise the login page redirects to the home page, and then we
                    # get back here and redirect to the login page.
                    if request.user.is_authenticated():
                        from django.contrib.auth import logout
                        from django.contrib import messages
                        logout(request)
                        messages.add_message(request, messages.ERROR, 'You are not a member of this organization.')

                    # The user isn't authenticated to see inside the organization subdomain.
                    allowed_paths = [reverse("account_login"), reverse("account_signup")]
                    if request.path not in allowed_paths:
                        # Redirect to the root of the domain where we'll show a login screen.
                        return HttpResponseRedirect(allowed_paths[0] + "?" + urlencode({ "next": request.path }))

                    # Let them through just when they're looking at the account login page.
                    return None

                # Ok, this request is good.

                # Set the Organiation on the request object.
                request.organization = org

                # Pre-load the user's settings task if the user is logged in,
                # so that we have global access to it.
                request.user.localize_to_org(request.organization)

                # Continue with normal request processing.
                return None

        # The HTTP host did not match a domain we can serve.
        # TODO: Replace with a nicer 404 page.
        return HttpResponse("There is no website at this address.", status=404)

