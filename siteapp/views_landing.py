# Views for q.govready.com, the special domain that just
# is a landing page and a way to create new organization
# subdomains.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

def homepage(request):
    # Main landing page.
    return render(request, "landing.html")

def aboutpage(request):
    # About page
    return render(request, "about.html")

