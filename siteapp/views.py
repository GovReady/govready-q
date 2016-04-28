from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from guidedmodules.models import Task

def homepage(request):
	if not request.user.is_authenticated():
		# Public homepage.
		return render(request, "index.html")

	elif not Task.has_completed_task(request.user, "account_settings"):
		# First task: Fill out your account settings.
		return HttpResponseRedirect(Task.get_task_for_module(request.user, "account_settings").get_absolute_url())

	else:
		# Ok, show user what they can do.
		return render(request, "home.html", {
			"tasks": Task.objects.filter(user=request.user).order_by('-updated'),
		})
