from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

import json

from .models import User
from guidedmodules.models import Task, ProjectMembership, Invitation
from questions import Module

def login_view(request, invitation=None):
    # when coming via an invitation confirmation page
    default_email = None
    if invitation:
        default_email = invitation.to_email or invitation.to_user.email

    # form definition (same form for both login and creating an account)
    import django.forms
    class AuthenticationForm(django.forms.Form):
        email = django.forms.EmailField(label='Email address')
        password = django.forms.CharField(label='Password', widget=django.forms.PasswordInput)

    # default instances
    new_user_form = AuthenticationForm(initial={
        "email": default_email
    })
    login_form = AuthenticationForm(initial={
        "email": default_email
    })

    if request.method == "POST":
        from django.contrib.auth import login, authenticate

        redirect_to = settings.LOGIN_REDIRECT_URL
        if invitation:
            redirect_to = invitation.get_acceptance_url() + "?auth=1"
        elif request.POST.get("next"):
            # TODO: Need to validate next?
            redirect_to = request.POST.get("next")

        if request.POST.get("method") == "login":
            login_form = AuthenticationForm(request.POST)
            if not login_form.errors:
                from .betteruser import LoginException
                try:
                    user = User.authenticate(login_form.cleaned_data['email'], login_form.cleaned_data['password'])
                    login(request, user)
                    return HttpResponseRedirect(redirect_to)
                except LoginException as e:
                    login_form.errors["email"] = [str(e)]

        else:
            # Create an account.
            new_user_form = AuthenticationForm(request.POST)
            if not new_user_form.errors:
                from email_validator import EmailNotValidError
                try:
                    # Create account.
                    user = User.get_or_create(new_user_form.cleaned_data['email'])
                    user.set_password(new_user_form.cleaned_data['password'])
                    user.save()

                    # Log user in.
                    user = authenticate(user_object=user)
                    login(request, user)
                    return HttpResponseRedirect(redirect_to)
                except EmailNotValidError as e:
                    new_user_form.errors["email"] = [str(e)]

    # Render.

    return render(request, "registration/login.html", {
        "next": request.GET.get("next"),
        "login_form": login_form,
        "new_user_form": new_user_form,
        "invitation": invitation,
    })


def homepage(request):
    if not request.user.is_authenticated():
        # Public homepage.
        return render(request, "index.html")

    elif not Task.has_completed_task(request.user, "account_settings"):
        # First task: Fill out your account settings.
        return HttpResponseRedirect(Task.get_task_for_module(request.user, "account_settings").get_absolute_url()
            + "/start")

    elif not Task.objects.filter(editor=request.user).exclude(project=None).exists() \
        and not ProjectMembership.objects.filter(user=request.user).exists():
        # Second task: Start a project if the user is not a member of any project
        # *and* the user is not editing any modules (they could be editing a module
        # in a project they are not a member of).
        return HttpResponseRedirect("/tasks/new-project")

    else:
        # Ok, show user what they can do.
        projects = [ ]
        for mbr in ProjectMembership.objects.filter(user=request.user).order_by('-project__created'):
            projects.append({
                "project": mbr.project,
                "tasks": Task.objects.filter(editor=request.user, project=mbr.project).order_by('-updated'),
                "others_tasks": Task.objects.filter(project=mbr.project).exclude(editor=request.user).order_by('-updated'),
                "open_invitations": Invitation.objects.filter(from_user=request.user, from_project=mbr.project, accepted_at=None, revoked_at=None).order_by('-created'),

                "startable_modules": Module.get_anserable_modules(),
                "send_invitation": json.dumps(Invitation.form_context_dict(request.user, mbr.project)),
            })

        # Add a fake project for system modules for this user.
        system_tasks = Task.objects.filter(editor=request.user, project=None)
        if len(system_tasks):
            projects.append({
                "tasks": system_tasks
            })

        return render(request, "home.html", {
            "answerable_modules": Module.get_anserable_modules(),
            "projects": projects,
        })

