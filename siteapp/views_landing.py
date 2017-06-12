# Views for q.govready.com, the special domain that just
# is a landing page and a way to create new organization
# subdomains.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django import forms
from django.conf import settings

from .models import Organization

def homepage(request):
    # Main landing page.

    from allauth.account.forms import SignupForm, LoginForm

    class NewOrgForm(forms.ModelForm):
        class Meta:
            model = Organization
            fields = ['name', 'subdomain']
            labels = {
                "name": "Organization Name",
                "subdomain": "Pick a web address",
            }
            help_texts = {
                "name": "",
                "subdomain": "Must be all lowercase and can contain letters, digits, and dashes.",
            }
            widgets = {
                "subdomain": forms.TextInput(attrs={"placeholder": "orgname", "addon_after": "." + settings.ORGANIZATION_PARENT_DOMAIN})
            }
        def clean_subdomain(self):
            # Not sure why the field validator isn't being run by the ModelForm.
            import re
            from .models import subdomain_regex
            from django.forms import ValidationError
            if not re.match(subdomain_regex, self.cleaned_data['subdomain']):
                raise ValidationError("The organization address must contain only lowercase letters, digits, and dashes and cannot start or end with a dash.")
            return self.cleaned_data['subdomain']

    signup_form = SignupForm()
    neworg_form = NewOrgForm()
    login_form = LoginForm()

    if request.POST.get("action") == "neworg":
        signup_form = SignupForm(request.POST)
        neworg_form = NewOrgForm(request.POST)
        if (request.user.is_authenticated or signup_form.is_valid()) and neworg_form.is_valid():
            # Perform signup and new org creation, then redirect
            # to that org.
            with transaction.atomic():
                if not request.user.is_authenticated:
                    # Create account.
                    user = signup_form.save(request)

                    # Log them in.
                    from django.contrib.auth import authenticate, login
                    user = authenticate(user_object=user)
                    login(request, user)
                else:
                    user = request.user
                org = Organization.create(admin_user=user, **neworg_form.cleaned_data)
                return HttpResponseRedirect("/welcome/" + org.subdomain)

    elif request.POST.get("action") == "login":
        login_form = LoginForm(request.POST, request=request)
        if login_form.is_valid():
            login_form.login(request)
            return HttpResponseRedirect('/') # reload

    elif request.POST.get("action") == "logout" and request.user.is_authenticated:
        from django.contrib.auth import logout
        logout(request)
        return HttpResponseRedirect('/') # reload

    return render(request, "landing.html", {
        "domain": settings.ORGANIZATION_PARENT_DOMAIN,
        "signup_form": signup_form,
        "neworg_form": neworg_form,
        "login_form": login_form,
        "member_of_orgs": Organization.get_all_readable_by(request.user) if request.user.is_authenticated else None,
    })

def org_welcome_page(request, org_slug):
    org = get_object_or_404(Organization, subdomain=org_slug)
    return render(request, "neworgwelcome.html", {
        "domain": settings.ORGANIZATION_PARENT_DOMAIN,
        "org": org,
    })    

from .notifications_helpers import notification_reply_email_hook