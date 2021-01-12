# Views for q.govready.com, the special domain that just
# is a landing page and a way to create new organization
# subdomains.

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.db import transaction
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from system_settings.models import SystemSettings
from .forms import PortfolioSignupForm
from .models import Organization, Portfolio, User
from .notifications_helpers import notification_reply_email_hook

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()
# logger = logging.getLogger(__name__)

LOGIN = "login"
SIGNUP = "signup"

def homepage(request):
    # Main landing page.

    from allauth.account.forms import SignupForm, LoginForm

    portfolio_form = PortfolioSignupForm()
    signup_form = SignupForm()
    login_form = LoginForm()

    # The allauth forms have 'autofocus' set on their widgets that draw the
    # focus in a way that doesn't make sense here.
    signup_form.fields['username'].widget.attrs.pop("autofocus", None)
    login_form.fields['login'].widget.attrs.pop("autofocus", None)

    if SIGNUP in request.path or request.POST.get("action") == SIGNUP:
        signup_form = SignupForm(request.POST)
        portfolio_form = PortfolioSignupForm(request.POST)
        if (request.user.is_authenticated or signup_form.is_valid()) and portfolio_form.is_valid():
            # Perform signup and new org creation, then redirect to main page
            with transaction.atomic():
                if not request.user.is_authenticated:
                    # Create account.
                    new_user = signup_form.save(request)
                    # Add default permission, view AppSource
                    new_user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
                    new_user.save()

                    # Log them in.
                    from django.contrib.auth import authenticate, login
                    user = authenticate(request, username=signup_form.cleaned_data['username'], password=signup_form.cleaned_data['password1'])
                    if user is not None:
                        login(request, user, 'django.contrib.auth.backends.ModelBackend')
                    else:
                        print("[ERROR] new_user '{}' did not authenticate after during account creation.".format(new_user.username))
                        messages.error(request, "[ERROR] new_user '{}' did not authenticate during account creation. Account not created. Report error to System Administrator. {}".format(new_user.username, vars(new_user)))
                        return HttpResponseRedirect("/")
                else:
                    user = request.user
                if portfolio_form.is_valid():
                    portfolio = portfolio_form.save()
                    portfolio.assign_owner_permissions(request.user)
                    logger.info(
                        event="new_portfolio",
                        object={"object": "portfolio", "id": portfolio.id, "title":portfolio.title},
                        user={"id": request.user.id, "username": request.user.username}
                    )
                    logger.info(
                        event="new_portfolio assign_owner_permissions",
                        object={"object": "portfolio", "id": portfolio.id, "title":portfolio.title},
                        receiving_user={"id": request.user.id, "username": request.user.username},
                        user={"id": request.user.id, "username": request.user.username}
                    )
                # Send a message to site administrators.
                from django.core.mail import mail_admins
                def subvars(s):
                    return s.format(
                        portfolio=portfolio.title,
                        username=user.username,
                        email=user.email,
                    )
                mail_admins(
                    subvars("New portfolio: {portfolio} (created by {email})"),
                    subvars("A new portfolio has been registered!\n\nPortfolio\n------------\nName: {portfolio}\nRegistering User\n----------------\nUsername: {username}\nEmail: {email}"))

                return HttpResponseRedirect("/projects")

    elif LOGIN in request.path or request.POST.get("action") == LOGIN:
        login_form = LoginForm(request.POST, request=request)
        if login_form.is_valid():
            login_form.login(request)
            return HttpResponseRedirect('/') # reload

    elif request.POST.get("action") == "logout" and request.user.is_authenticated:
        from django.contrib.auth import logout
        logout(request)
        return HttpResponseRedirect('/') # reload

    return render(request, "index.html", {
        "hide_registration": SystemSettings.hide_registration,
        "signup_form": signup_form,
        "portfolio_form": portfolio_form,
        "login_form": login_form,
        "member_of_orgs": Organization.get_all_readable_by(request.user) if request.user.is_authenticated else None,
    })

def org_group_projects(request, org_slug):
    """Get projects belonging to group"""
    org = get_object_or_404(Organization, slug=org_slug)
    projects = org.get_projects()
    return render(request, "org_groups/org_group.html", {
        "org": org,
        "projects": projects,
    })

@login_required
def user_profile_photo(request, user_id, hash):
    # Get the User's profile photo for the specified organization.
    # To prevent enumeration of User info, we expect a hash value
    # in the URL that we compare against the User's current photo.
    # Raises 404 on any request that doesn't work out to prevent
    # enumeration of Organization subdomains too.
    user = get_object_or_404(User, id=user_id)
    prj = user.get_account_project()
    try:
        account_settings = prj.root_task.get_or_create_subtask(user, "account_settings", create=False)
        photo = account_settings.get_answers().get("picture")
    except:
        raise Http404()
    if not photo: raise Http404()
    if not photo.answered_by_file.name: raise Http404()

    # Check that the fingerprint in the URL matches. See User.get_profile_picture_absolute_url.
    user.preload_profile()
    path_with_fingerprint = user.get_profile_picture_absolute_url()
    if not path_with_fingerprint.endswith(request.path):
        raise Http404()

    # Get the dbstorage.models.StoredFile instance which holds
    # an auto-detected mime type.
    from dbstorage.models import StoredFile
    sf = StoredFile.objects.only("mime_type").get(path=photo.answered_by_file.name)
    mime_type = sf.mime_type
    if not mime_type.startswith("image/"): raise Http404() # not an image, not safe to serve

    # Serve the image.
    import os.path
    resp = HttpResponse(photo.answered_by_file, content_type=mime_type)
    resp['Content-Disposition'] = 'inline; filename=' + user.username + "_" + os.path.basename(photo.answered_by_file.name)
    return resp

# TODO: Make groups available to all after managing group membership
@login_required
def org_groups(request):
    """List org groups"""

    return render(request, "org_groups/org_groups.html", {
        "org_groups": Organization.get_all_readable_by(request.user) if request.user.is_authenticated else None,
    })

@login_required
def new_org_group(request):
    # Create new organization group

    class NewOrgForm(forms.ModelForm):
        class Meta:
            model = Organization
            fields = ['name', 'slug']
            labels = {
                "name": "Group name",
                "slug": "Group \"slug\" to appear in URLs",
            }
            help_texts = {
                "name": "An organizational group for you teams assessments.",
                "slug": "Only lowercase letters, digits, and dashes.",
            }
            widgets = {
                "name": forms.TextInput(attrs={"placeholder": "Privacy Office"}),
                "slug": forms.TextInput(attrs={"placeholder": "privacy"})
            }

        def clean_slug(self):
            # Not sure why the field validator isn't being run by the ModelForm.
            import re
            from .models import subdomain_regex
            from django.forms import ValidationError
            if not re.match(subdomain_regex, self.cleaned_data['slug']):
                raise ValidationError("The organization address must contain only lowercase letters, digits, and dashes and cannot start or end with a dash.")
            return self.cleaned_data['slug']

    neworg_form = NewOrgForm()

    if request.POST.get("action") == "neworg":
        # signup_form = SignupForm(request.POST)
        neworg_form = NewOrgForm(request.POST)
        if request.user.is_authenticated and neworg_form.is_valid():
            # Perform new org group creation, then redirect
            # to that org group.
            with transaction.atomic():
                if not request.user.is_authenticated:
                    # TODO Log message that usunloged in user tried to create a group
                    return HttpResponseRedirect("/")
                else:
                    user = request.user
                org = Organization.create(admin_user=user, **neworg_form.cleaned_data)
                return HttpResponseRedirect("/" + org.slug + "/projects")

    return render(request, "org_groups/new_org_group.html", {
        "neworg_form": neworg_form,
        # "member_of_orgs": Organization.get_all_readable_by(request.user) if request.user.is_authenticated else None,
    })


@csrf_exempt
def project_api(request, project_id):
    from collections import OrderedDict

    # Get user from API key.
    api_key = request.META.get("HTTP_AUTHORIZATION", "").strip()
    if len(api_key) < 32: # prevent null values from matching against users without api keys
        return JsonResponse(OrderedDict([("status", "error"), ("error", "An API key was not present in the Authorization header.")]), json_dumps_params={ "indent": 2 }, status=403)

    from django.db.models import Q
    from .models import User, Project
    
    try:
        user = User.objects.get(Q(api_key_rw=api_key)|Q(api_key_ro=api_key)|Q(api_key_wo=api_key))
    except User.DoesNotExist:
        return JsonResponse(OrderedDict([("status", "error"), ("error", "A valid API key was not present in the Authorization header.")]), json_dumps_params={ "indent": 2 }, status=403)

    # Get project and check authorization.
    project = get_object_or_404(Project, id=project_id)
    if not project.has_read_priv(user):
        return JsonResponse(OrderedDict([("status", "error"), ("error", "The user associated with the API key does not have read perission on the project.")]), json_dumps_params={ "indent": 2 }, status=403)

    if request.method == "GET":
        # Export data.
        value = project.export_json(include_file_content=False, include_metadata=False)

        # Return the value as JSON.
        return JsonResponse(value, json_dumps_params={ "indent": 2 })

    elif request.method == "POST":
        # Update the value.

        # Check that the API key has write access.
        if not project.root_task.has_write_priv(user):
            return JsonResponse(OrderedDict([("status", "error"), ("error", "The user associated with the API key does not have write perission on the project.")]), json_dumps_params={ "indent": 2 }, status=403)
        if api_key not in (user.api_key_rw, user.api_key_wo):
            return JsonResponse(OrderedDict([("status", "error"), ("error", "The API key does not have write perission on the project.")]), json_dumps_params={ "indent": 2 }, status=403)

        # Parse the new project body.
        if request.META.get("CONTENT_TYPE") == "application/json":
            # A JSON object is given in the import/export format. Parse it.
            import json
            try:
                value = json.loads(request.body.decode("utf-8"))
            except json.decoder.JSONDecodeError as e:
                return JsonResponse(OrderedDict([("status", "error"), ("error", "Invalid JSON in request body. " + str(e))]), json_dumps_params={ "indent": 2 }, status=400)

            # Update.
            log = []
            ok = project.import_json(value, user, "api", lambda msg : log.append(msg))

        else:
            # Form fields are given in POST and FILES. Process each item...

            from guidedmodules.models import TaskAnswer
            from guidedmodules.answer_validation import question_input_parser, validator
            import django.core.files.uploadedfile

            # For each item...
            log = []
            ok = True
            subtasks = { }
            for key, v in list(request.POST.lists()) + list(request.FILES.items()):
                try:
                    # The item is a dotted path of project + question IDs to the
                    # question to update. Follow the path to find the Task and ModuleQuestion
                    # to update. Start with the project root task, then for each item in the path...
                    task = project.root_task
                    question = None
                    if not key.startswith("project."): raise ValueError("Invalid question ID: " + key)
                    for i, pathitem in enumerate(key.split(".")[1:]):
                        # If this is not the first item, then in the last iteration we
                        # were left with a Task and a ModuleQuestion in that task. Since
                        # we've continued with another dot and path part, the last ModuleQuestion
                        # must have been a module-type question. Move to its *answer*,
                        # which is another Task.
                        if question is not None:
                            # Only module-type questions have subtasks.
                            if question.spec["type"] not in ("module", "module-set"):
                                raise ValueError("Invalid question ID: {}. {} does not refer to a task that has sub-answers.".format(
                                    key,
                                    ".".join(key.split(".")[:i+1]),
                                    ))

                            # If we've already traversed this path in a previous field,
                            # use the same Task. For module-type questions, this acts as
                            # a cache and saves us a database query. For module-set questions,
                            # this ensures we create just one subtask for this path for
                            # this POST request and share it across all POST parameters that
                            # use this path.
                            if (task, question) in subtasks:
                                task = subtasks[(task, question)]
                            else:
                                # If we haven't seen this path yet, query for the subtask
                                try:
                                    subtask = task.get_or_create_subtask(user, question)
                                except ValueError:
                                    # Raised if the question is not answered and the question uses
                                    # a protocol for selecting compliance apps rather than specifying
                                    # a concrete Module to use for answers. In this case, we can't
                                    # start a Task implicitly.
                                    raise ValueError("Invalid question ID '{}': {} has not been answered yet by a compliance app so its data fields cannot be set.".format(
                                        key,
                                        ".".join(key.split(".")[:i+1])
                                    ))

                                if hasattr(subtask, 'was_just_created_by_get_or_create_subtask'):
                                    log.append("Creating new answer to {}.".format(question.spec['title']))

                                # Save to cache for this request and move forward.
                                subtasks[(task, question)] = subtask
                                task = subtask

                        # Get the question this corresponds to within the task
                        question = task.module.questions.filter(key=pathitem).first()
                        if not question:
                            raise ValueError("Invalid question ID: {}. '{}' is not a question in {}.".format(
                                key,
                                pathitem,
                                task.module.spec['title']))

                    # Parse and validate the answer.
                    v = question_input_parser.parse(question, v)
                    v = validator.validate(question, v)

                    # Save.
                    v_file = None
                    if question.spec["type"] == "file":
                        v_file = v
                        v = None
                    ta, _ = TaskAnswer.objects.get_or_create(task=task, question=question)
                    saved = ta.save_answer(v, [], v_file, user, "api")
                    if saved:
                        log.append(key + " updated")
                    else:
                        log.append(key + " unchanged")
                
                except ValueError as e:
                    log.append(key + ": " + str(e))
                    ok = False


        return JsonResponse(OrderedDict([
            ("status", "ok" if ok else "error"),
            ("details", log),
        ]), json_dumps_params={ "indent": 2 })
