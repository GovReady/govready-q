from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from guidedmodules.models import Task, ProjectMembership

def homepage(request):
	if not request.user.is_authenticated():
		# Public homepage.
		return render(request, "index.html")

	elif not Task.has_completed_task(request.user, "account_settings"):
		# First task: Fill out your account settings.
		return HttpResponseRedirect(Task.get_task_for_module(request.user, "account_settings").get_absolute_url())

	elif not ProjectMembership.objects.filter(user=request.user).exists():
		# Second task: Create a Project.
		return HttpResponseRedirect("/tasks/new-project")

	else:
		# Ok, show user what they can do.
		projects = [ ]
		for mbr in ProjectMembership.objects.filter(user=request.user).order_by('-project__created'):
			projects.append({
				"project": mbr.project,
				"tasks": Task.objects.filter(editor=request.user, project=mbr.project).order_by('-updated')
			})

		# Add a fake project for system modules for this user.
		system_tasks = Task.objects.filter(editor=request.user, project=None)
		if len(system_tasks):
			projects.append({
				"tasks": system_tasks
			})

		return render(request, "home.html", {
			"projects": projects,
		})

from django.contrib.auth.backends import ModelBackend
class DirectLoginBackend(ModelBackend):
	# Register in settings.py!
	# Django can't log a user in without their password. Before they create
	# a password, we use this to log them in. Registered in settings.py.
	supports_object_permissions = False
	supports_anonymous_user = False
	def authenticate(self, user_object=None):
		return user_object
