# Views for q.govready.com, the special domain that just
# is a landing page and a way to create new organization
# subdomains.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
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

    # The allauth forms have 'autofocus' set on their widgets that draw the
    # focus in a way that doesn't make sense here.
    signup_form.fields['username'].widget.attrs.pop("autofocus", None)
    login_form.fields['login'].widget.attrs.pop("autofocus", None)

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

@csrf_exempt
def project_api(request, org_slug, project_id):
    from collections import OrderedDict

    # Get user from API key.
    api_key = request.META.get("HTTP_AUTHORIZATION", "").strip()
    if len(api_key) < 32: # prevent null values from matching against users without api keys
        return JsonResponse(OrderedDict([("status", "error"), ("error", "An API key was not present in the Authorization header.")]), json_dumps_params={ "indent": 2 }, status=403)

    from django.db.models import Q
    from .models import User, Project
    
    try:
        user = User.objects.get(Q(api_key_rw=api_key)|Q(api_key_ro=api_key))
    except User.DoesNotExist:
        return JsonResponse(OrderedDict([("status", "error"), ("error", "A valid API key was not present in the Authorization header.")]), json_dumps_params={ "indent": 2 }, status=403)

    # Get project and check authorization.
    organization = get_object_or_404(Organization, subdomain=org_slug)
    project = get_object_or_404(Project, id=project_id, organization=organization)
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
        if api_key != user.api_key_rw:
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

            log = []
            ok = True
            for key, v in list(request.POST.lists()) + list(request.FILES.items()):
                try:
                    # Find the Task and ModuleQuestion that corresponds to
                    # this key-value pair.
                    task = project.root_task
                    question = None
                    if not key.startswith("project."): raise ValueError("Invalid question ID: " + key)
                    for pathitem in key.split(".")[1:]:
                        # Advance to the task pointed to by the last question.
                        if question is not None:
                            if question.spec["type"] != "module": raise ValueError("Invalid question ID: " + key)
                            ta = task.answers.filter(question=question).first()
                            if ta is None: raise ValueError("Invalid question ID (question on path is not answered yet): " + key)
                            a = ta.get_current_answer()
                            if not a or a.cleared: raise ValueError("Invalid question ID (question on path is not answered yet): " + key)
                            task = a.answered_by_task.first()

                        # Get the question this corresponds to within the task
                        question = task.module.questions.filter(key=pathitem).first()
                        if not question: raise ValueError("Invalid question ID: " + key)

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
