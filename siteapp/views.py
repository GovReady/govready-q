from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

import json

from .models import User, Project, Invitation
from guidedmodules.models import Module, Task, ProjectMembership
from discussion.models import Discussion

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
                from .betteruser import CreateUserException
                try:
                    # Create account.
                    user = User.create(new_user_form.cleaned_data['email'], new_user_form.cleaned_data['password'])
                    user.save()

                    # Log user in.
                    user = authenticate(user_object=user)
                    login(request, user)
                    return HttpResponseRedirect(redirect_to)
                except (EmailNotValidError, CreateUserException) as e:
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

    else:
        # Ok, show user what they can do --- list the projects they
        # are involved with.
        projects = set()

        # Add all of the Projects the user is a member of.
        for pm in ProjectMembership.objects.filter(user=request.user):
            projects.add(pm.project)
            if pm.is_admin:
                # Annotate with whether the user is an admin of the project.
                pm.project.user_is_admin = True

        # Add projects that the user is the editor of a task in, even if
        # the user isn't a team member of that project.
        for task in Task.get_all_tasks_readable_by(request.user).order_by('-created'):
            projects.add(task.project)

        # Add projects that the user is participating in a Discussion in
        # as a guest.
        for d in Discussion.objects.filter(guests=request.user):
            projects.add(d.attached_to.task.project)

        # Sort.
        projects = sorted(projects, key = lambda x : (x is not None, x.updated if x else None), reverse=True)

        return render(request, "home.html", {
            "projects": projects,
            "any_have_members_besides_me": ProjectMembership.objects.filter(project__in=projects).exclude(user=request.user),
        })


@login_required
def project(request, project_id=None):
    if project_id != None:
        project = get_object_or_404(Project, id=project_id)
    else:
        # The "None" project represents the container for the user's
        # system account modules.
        project = None

    if project:
        # Check authorization.
        if not project.has_read_priv(request.user):
            return HttpResponseForbidden()

        # Redirect if slug is not canonical. We do this after checking for
        # read privs so that we don't reveal the task's slug to unpriv'd users.
        if request.path != project.get_absolute_url():
            return HttpResponseRedirect(task.get_absolute_url())

    ret = {
        "is_admin": not project or request.user in project.get_admins(),
        "can_begin_module": project and request.user in project.get_admins(),
        "project_has_members_besides_me": project.members.exclude(user=request.user),
        "project": project,
        "title": project.title if project else "System Account",
        "tasks": Task.get_all_tasks_readable_by(request.user).filter(editor=request.user, project=project),
        "others_tasks": Task.get_all_tasks_readable_by(request.user).filter(project=project).exclude(editor=request.user),
    }

    if project:
        ret.update({
            "discussions": list(project.get_discussions_in_project_as_guest(request.user)),
            "open_invitations": [
                inv for inv in Invitation.objects.filter(from_user=request.user, from_project=project, accepted_at=None, revoked_at=None).order_by('-created')
                if not inv.is_expired() ],
            "startable_modules": Module.get_startable_modules(),
            "send_invitation": json.dumps(Invitation.form_context_dict(request.user, project)),
        })

    return render(request, "project.html", ret)

# INVITATIONS

@login_required
def send_invitation(request):
    import email_validator
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    try:
        if not request.POST['user_id'] and not request.POST['user_email']:
            raise ValueError("Select a team member or enter an email address.")

        if request.POST['user_email']:
            email_validator.validate_email(request.POST['user_email'])

        # Validate that the user is a member of from_project. Is None
        # if user is not a project member.
        from_project = Project.objects.filter(id=request.POST["project"], members__user=request.user).first()

        # Authorization for adding invitee to the project team.
        if not from_project:
            into_project = False
        else:
            inv_ctx = Invitation.form_context_dict(request.user, from_project)
            into_project = (request.POST.get("add_to_team", "") != "") and inv_ctx["can_add_invitee_to_team"]

        # Target.
        if request.POST.get("into_new_task_module_id"):
            target = from_project
            target_info = {
                "into_new_task_module_id": Module.objects.filter(id=request.POST.get("into_new_task_module_id")).first().id,
            }

        elif request.POST.get("into_task_editorship"):
            target = Task.objects.get(id=request.POST["into_task_editorship"])
            if target.editor != request.user:
                raise HttpResponseForbidden()
            if from_project and target.project != from_project:
                return HttpResponseForbidden()

            # from_project may be None if the requesting user isn't a project
            # member, but they may transfer editorship and so in that case we'll
            # set from_project to the Task's project
            from_project = target.project
            target_info =  {
                "what": "editor",
            }

        elif "into_discussion" in request.POST:
            target = get_object_or_404(Discussion, id=request.POST["into_discussion"])
            if not target.can_invite_guests(request.user):
                return HttpResponseForbidden()
            target_info = {
                "what": "invite-guest",
            }

        else:
            target = from_project
            target_info = {
                "what": "join-team",
            }

        inv = Invitation.objects.create(
            # who is sending the invitation?
            from_user=request.user,
            from_project=from_project,

            # what is the recipient being invited to? validate that the user is an admin of this project
            # or an editor of the task being reassigned.
            into_project=into_project,
            target=target,
            target_info=target_info,

            # who is the recipient of the invitation?
            to_user=User.objects.get(id=request.POST["user_id"]) if request.POST.get("user_id") else None,
            to_email=request.POST.get("user_email"),

            # personalization
            text=request.POST.get("message", ""),
            email_invitation_code=Invitation.generate_email_invitation_code(),
        )

        inv.send() # TODO: Move this into an asynchronous queue.

        return JsonResponse({ "status": "ok" })

    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })
    except Exception as e:
        import sys
        sys.stderr.write(str(e) + "\n")
        return JsonResponse({ "status": "error", "message": "There was a problem -- sorry!" })

@login_required
def cancel_invitation(request):
    inv = get_object_or_404(Invitation, id=request.POST['id'], from_user=request.user)
    inv.revoked_at = timezone.now()
    inv.save(update_fields=['revoked_at'])
    return JsonResponse({ "status": "ok" })

def accept_invitation(request, code=None):
    assert code.strip() != ""
    inv = get_object_or_404(Invitation, email_invitation_code=code)

    from django.contrib.auth import authenticate, login, logout
    from django.contrib import messages
    from django.http import HttpResponseRedirect
    import urllib.parse

    # If this is a repeat-click, just redirect the user to where
    # they went the first time.
    if inv.accepted_at:
        return HttpResponseRedirect(inv.get_redirect_url())

    # Can't accept if this object has expired. Warn the user but
    # send them to the homepage.
    if inv.is_expired():
        messages.add_message(request, messages.ERROR, 'The invitation you wanted to accept has expired.')
        return HttpResponseRedirect("/")

    # Get the user logged into an account.
    
    matched_user = inv.to_user \
        or User.objects.filter(email=inv.to_email).exclude(id=inv.from_user.id).first()
    
    if request.user.is_authenticated() and request.GET.get("auth") == "1":
        # The user is logged in and the "auth" flag is set, so let the user
        # continue under this account. This code path occurs when the user
        # first reaches this view but is not authenticated as the user that
        # was invited. We then send them to create an account or log in.
        # The "next" URL on that login screen adds "auth=1", so that when
        # we come back here, we just accept whatever account they created
        # or logged in to. The meaning of "auth" is the User's desire to
        # continue with their existing credentials. We don't go through
        # this path on the first run because the user may not want to
        # accept the invitation under an account they happened to be logged
        # in as.
        pass

    elif matched_user and request.user == matched_user:
        # If the invitation was to a user account, and the user is already logged
        # in to it, then we're all set. Or if the invitation was sent to an email
        # address already associated with a User account and the user is logged
        # into that account, then we're all set.
        pass

    elif matched_user:
        # If the invitation was to a user account or to an email address that has
        # an account, but the user wasn't already logged in under that account,
        # then since the user on this request has just demonstrated ownership of
        # that user's email address, we can log them in immediately.
        matched_user = authenticate(user_object=matched_user)
        if not matched_user.is_active:
            messages.add_message(request, messages.ERROR, 'Your account has been deactivated.')
            return HttpResponseRedirect("/")
        if request.user.is_authenticated():
            # The user was logged into a different account before. Log them out
            # of that account and then log them into the account in the invitation.
            logout(request) # setting a message after logout but before login should keep the message in the session
            messages.add_message(request, messages.INFO, 'You have been logged in as %s.' % matched_user)
        login(request, matched_user)

    else:
        # The invitation was sent to an email address that does not have a matching
        # User account. Ask the user to log in or sign up, using a redirect to the
        # login page, with a next URL set to take them back to this step. In the
        # event the user was logged in (and we didn't handle it above), log them
        # out and force them to log into a new account.
        from siteapp.views import login_view
        logout(request)
        return login_view(request, invitation=inv)

    # The user is now logged in and able to accept the invitation.
    with transaction.atomic():

        inv.accepted_at = timezone.now()
        inv.accepted_user = request.user

        def add_message(message):
            messages.add_message(request, messages.INFO, message)

        # Add user to a project team.
        if inv.into_project:
            ProjectMembership.objects.create(
                project=inv.from_project,
                user=request.user,
                )
            add_message('You have joined the team %s.' % inv.from_project.title)

        # Run the target's invitation accept function.
        inv.target.accept_invitation(inv, add_message)

        # Update this invitation.
        inv.save()

        # TODO: Notify inv.from_user that the invitation was accepted.
        #       Create other notifications?

        return HttpResponseRedirect(inv.get_redirect_url())
