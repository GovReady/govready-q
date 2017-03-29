from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import User, Folder, Project, Invitation
from guidedmodules.models import Module, Task, ProjectMembership
from discussion.models import Discussion

from .good_settings_helpers import AllauthAccountAdapter # ensure monkey-patch is loaded
from .notifications_helpers import *

def homepage(request):
    from allauth.account.forms import LoginForm
    return render(request, "index.html", {
        "has_projects": (len(Project.get_projects_with_read_priv(request.user, request.organization)) > 0)
            if hasattr(request, 'organization') else False,
        "login_form": LoginForm,
    })

def project_list(request):
    # Get the projects.
    projects = Project.get_projects_with_read_priv(request.user, request.organization)
    for p in projects:
        p.open_tasks = p.get_open_tasks(request.user) # for the template

    # Collate into folders. Folders are accessible to a user
    # just when they can see a Project within it, so we go
    # backwards from Projects to Folders.
    folders = list(
        (Folder.objects.filter(projects__in=projects)
            | Folder.objects.filter(admin_users=request.user))
          .distinct())

    for folder in folders:
        # Set an attribute on the Folder with a list of
        # projects that the user has access to.
        projects_in_folder = set(folder.projects.all())
        folder.accessible_projects = [p for p in projects if p in projects_in_folder]

        # Mark folders that the user is an admin of, i.e. can rename it and
        # see all projects within it.
        folder.is_admin = (request.user in folder.get_admins())

        # If the user is an admin and there are projects in the folder the
        # user can't see, mark that too.
        if folder.is_admin:
            folder.num_hidden_projects = len(projects_in_folder - set(folder.accessible_projects))

    # Sort the folders by the sort order of the first project
    # in each folder.
    folders.sort(key = lambda folder : [projects.index(p) for p in folder.accessible_projects])

    return render(request, "project_list.html", {
        "folders": folders,
        "any_have_members_besides_me": ProjectMembership.objects.filter(project__in=projects).exclude(user=request.user),
    })

def add_assessment_catalog_metadata(module):
    from guidedmodules.module_logic import render_content

    module.short_description = render_content(
        {
            "template": module.spec.get("catalog", {}).get("description", {}).get("short") or "",
            "format": "markdown",
        },
        None,
        "html",
        "%s %s" % (repr(module), "short description")
    )

    module.long_description = render_content(
        {
            "template": module.spec.get("catalog", {}).get("description", {}).get("long")
                        or module.spec.get("catalog", {}).get("description", {}).get("short")
                        or "",
            "format": "markdown",
        },
        None,
        "html",
        "%s %s" % (repr(module), "short description")
    )

@login_required
def assessment_catalog(request):
    # Get the project-type modules that the user(+org) has permission to start.
    project_modules = Module.get_all_startable_projects(request.user, request.organization)

    # Add some extra fields for the template.
    for m in project_modules:
        add_assessment_catalog_metadata(m)

    return render(request, "assessment-catalog.html", {
        "project_modules": project_modules,
    })

@login_required
def assessment_catalog_item(request, module_key):
    # Is this a module the user has access to?
    project_modules = Module.get_all_startable_projects(request.user, request.organization)
    module = [m for m in project_modules if m.key == module_key]
    if len(module) != 1: raise Http404()
    module = module[0]

    # Add some extra fields for the template.
    add_assessment_catalog_metadata(module)

    if request.method == "GET":
        # Show the assessment "app" page.

        return render(request, "assessment-catalog-item.html", {
            "first": not ProjectMembership.objects.filter(user=request.user, project__organization=request.organization).exists(),
            "module": module,
        })
    
    else:
        # Show the form to start the assessment.

        from django.forms import ModelForm, ChoiceField, RadioSelect, MultipleChoiceField, \
            CheckboxSelectMultiple, CharField, Textarea
        from django.core.exceptions import ValidationError

        # What Folders can the new Project be added to?
        folders = list(Folder.get_all_folders_admin_of(request.user, request.organization))

        def validate_list_of_email_addresses(value):
            # This is a form validator as well as a function to return the split and
            # normalized addresses.
            def validate_email(email):
                import email_validator
                try:
                    return email_validator.validate_email(email)["email"]
                except ValueError as e:
                    raise ValidationError(email + ": " + str(e))
            import re
            return set(
                validate_email(email)
                for email in re.split(r"[\s,]+", value)
                if email != "") # if value is the empty string, we will get one empty value after split

        # The form.
        class NewProjectForm(ModelForm):
            class Meta:
                model = Project
                fields = []

            if len(folders) > 0:
                add_to_folder = ChoiceField(
                    choices=[(f.id, f) for f in folders] + [("", "Add to New Folder")],
                    required=False,
                    label="Add this assessment to a folder:",
                    widget=RadioSelect)

        if "firstsubmit" in request.POST:
            # When coming to this page for the first time, don't do validation since
            # nothing has been submitted yet.
            form = NewProjectForm()
        else:
            form = NewProjectForm(request.POST)
            if not form.errors:
                with transaction.atomic():
                    # Get or create the Folder the new Project is going into.
                    # (The form field isn't shown if there are no existing folders
                    # (get returns None), and if the user wants to create a new folder
                    # the value is the empty string, otherwise it is a string containing
                    # a primary key (positive integer).)
                    if form.cleaned_data.get("add_to_folder"):
                        folder = Folder.objects.get(id=form.cleaned_data["add_to_folder"])
                    else:
                        folder = Folder.objects.create(
                            organization=request.organization,
                            title="New Folder")

                    # create project
                    project = form.save(commit=False)
                    project.organization = request.organization

                    # assign a good title
                    project.title = module.title
                    projects_in_folder = folder.get_readable_projects(request.user)
                    existing_project_titles = [p.title for p in projects_in_folder]
                    ctr = 0
                    while project.title in existing_project_titles:
                        ctr += 1
                        project.title = module.title + " " + str(ctr)

                    # save and add to folder
                    project.save()
                    project.set_root_task(module, request.user)
                    folder.projects.add(project)

                    # add user as an admin
                    ProjectMembership.objects.create(
                        project=project,
                        user=request.user,
                        is_admin=True)

                return HttpResponseRedirect(project.get_absolute_url())

        return render(request, "assessment-catalog-item-start.html", {
            "module": module,
            "form": form,
        })

@login_required
def project(request, project_id):
    project = get_object_or_404(Project, id=project_id, organization=request.organization)

    # Check authorization.
    if not project.has_read_priv(request.user):
        return HttpResponseForbidden()

    # Redirect if slug is not canonical. We do this after checking for
    # read privs so that we don't reveal the task's slug to unpriv'd users.
    if request.path != project.get_absolute_url():
        return HttpResponseRedirect(project.get_absolute_url())

    # Get all of the discussions I'm participating in as a guest in this project.
    # Meaning, I'm not a member, but I still need access to certain tasks and
    # certain questions within those tasks.
    discussions = list(project.get_discussions_in_project_as_guest(request.user))

    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    root_task_answers = project.root_task.get_answers()
    root_task_answers = root_task_answers.with_extended_info()

    can_begin_module = project.can_start_task(request.user)

    # Create all of the module entries in a tabs & groups data structure.
    from collections import OrderedDict
    tabs = OrderedDict()
    action_buttons = []
    question_dict = { }
    first_start = True
    for mq in project.root_task.module.questions.all().order_by('definition_order'):
        # Display module/module-set questions only. Other question types in a project
        # module are not valid.
        if mq.spec.get("type") not in ("module", "module-set"):
            continue

        # Skip questions that are imputed.
        if mq.key in root_task_answers.was_imputed:
            continue

        # Is this question answered yet? Are there any discussions the user
        # is a guest of in any of the tasks that answer this question?
        is_finished = None
        tasks = []
        task_discussions = []
        ans = root_task_answers.as_dict().get(mq.key)
        if ans is not None:
            if mq.spec["type"] == "module":
                # Convert a ModuleAnswers instance to an array containing just itself.
                ans = [ans]
            elif mq.spec["type"] == "module-set":
                # ans is already a list of ModuleAnswers instances.
                pass
            for module_answers in ans:
                task = module_answers.task

                task_discussions.extend([d for d in discussions if d.attached_to.task == task])
                
                if not task.has_read_priv(request.user):
                    continue

                tasks.append(task)
                task.has_write_priv = task.has_write_priv(request.user)
                if not task.is_finished():
                    # If any task is unfinished, the whole question
                    # is marked as unfinished.
                    is_finished = False
                elif is_finished is None:
                    # If all tasks are finished, the whole question
                    # is marked as finished.
                    is_finished = True

        # Do not display if the user can't start a task and there are no
        # tasks visible to the user.
        if not can_begin_module and len(tasks) == 0 and len(task_discussions) == 0:
            continue

        # Is this the first Start?
        d_first_start = first_start and (len(tasks) == 0)
        if d_first_start: first_start = False

        # Create template context dict.
        d = {
            "question": mq,
            "module": mq.answer_type_module,
            "is_finished": is_finished,
            "tasks": tasks,
            "can_start_new_task": mq.spec["type"] == "module-set" or len(tasks) == 0,
            "first_start": d_first_start,
            "discussions": task_discussions,
            "invitations": [], # filled in below
        }
        question_dict[mq.id] = d

        if mq.spec.get("placement", "tabpanel") == "tabpanel":
            # Create the tab and group for this.
            tabname = mq.spec.get("tab", "Modules")
            tab = tabs.setdefault(tabname, {
                "title": tabname,
                "unfinished_tasks": 0,
                "groups": OrderedDict(),
            })
            groupname = mq.spec.get("group", "Modules")
            group = tab["groups"].setdefault(groupname, {
                "title": groupname,
                "modules": [],
            })
            group["modules"].append(d)

            # Add a flag to the tab if any tasks contained
            # within it are unfinished.
            for t in tasks:
                if not t.is_finished():
                    tab["unfinished_tasks"] += 1

        elif mq.spec.get("placement") == "action-buttons":
            action_buttons.append(d)

    # Find any open invitations and if they are for particular modules,
    # display them with the module.
    other_open_invitations = []
    for inv in Invitation.objects.filter(from_user=request.user, from_project=project, accepted_at=None, revoked_at=None).order_by('-created'):
        if inv.is_expired():
            continue
        if inv.target == project:
            into_new_task_question_id = inv.target_info.get("into_new_task_question_id")
            if into_new_task_question_id:
                if into_new_task_question_id in question_dict: # should always be True
                    question_dict[into_new_task_question_id]["invitations"].append(inv)
                    continue

        # If the invitation didn't get put elsewhere, display in the
        # other list.                
        other_open_invitations.append(inv)

    # Additional tabs of content.
    additional_tabs = []
    if project.root_task.module.spec.get("output"):
        for doc in project.root_task.render_output_documents():
            if doc.get("tab") in tabs:
                # Assign this to one of the tabs.
                tabs[doc["tab"]]["intro"] = doc
            else:
                # Add tab to end.
                additional_tabs.append(doc)

    # Render.
    return render(request, "project.html", {
        "is_admin": request.user in project.get_admins(),
        "can_begin_module": can_begin_module,
        "project": project,
        "title": project.title,
        "intro" : project.root_task.render_field('introduction') if project.root_task.module.spec.get("introduction") else "",
        "additional_tabs": additional_tabs,
        "open_invitations": other_open_invitations,
        "send_invitation": Invitation.form_context_dict(request.user, project, [request.user]),
        "tabs": list(tabs.values()),
        "action_buttons": action_buttons,
    })


@login_required
def new_folder(request):
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    f = Folder.objects.create(
        organization=request.organization,
        title=request.POST.get("title") or "New Folder",
    )
    f.admin_users.add(request.user)
    return JsonResponse({ "status": "ok", "id": f.id, "title": f.title })

@login_required
def rename_folder(request):
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])

    # Get the folder.
    folder = get_object_or_404(Folder, id=request.POST.get("folder"))

    # Validate that the user can rename it.
    if request.user not in folder.get_admins():
        return JsonResponse({ "status": "error", "message": "Not authorized." })

    # Update.
    folder.title = request.POST.get("title")
    folder.save()
    return JsonResponse({ "status": "ok" })


@login_required
def delete_folder(request):
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])

    # Get the folder.
    folder = get_object_or_404(Folder, id=request.POST.get("folder"))

    # Validate that the user can rename it.
    if request.user not in folder.get_admins():
        return JsonResponse({ "status": "error", "message": "Not authorized." })
    if folder.projects.count() > 0:
        return JsonResponse({ "status": "error", "message": "The folder is not empty." })

    # Delete.
    folder.delete()
    return JsonResponse({ "status": "ok" })

def project_admin_login_post_required(f):
    # Wrap the function to do authorization and change arguments.
    def g(request, project_id):
        # Get project, check authorization.
        project = get_object_or_404(Project, id=project_id, organization=request.organization)
        if request.user not in project.get_admins():
            return HttpResponseForbidden()

        # Call function with changed argument.
        return f(request, project)

    # Apply the require_http_methods decorator.
    g = require_http_methods(["POST"])(g)

    # Apply the login_required decorator.
    g = login_required(g)

    return g

@project_admin_login_post_required
def delete_project(request, project):
    if not project.is_deletable():
        return JsonResponse({ "status": "error", "message": "This project cannot be deleted." })
    project.delete()
    return JsonResponse({ "status": "ok" })

@project_admin_login_post_required
def export_project(request, project):
    from urllib.parse import quote
    resp = JsonResponse(project.export_json(), json_dumps_params={"indent": 2})
    resp["content-disposition"] = "attachment; filename=%s.json" % quote(project.title)
    return resp

@project_admin_login_post_required
def import_project_data(request, project):
    # Deserialize the JSON from request.FILES. Assume the JSON data is
    # UTF-8 encoded and ensure dicts are parsed as OrderedDict so that
    # key order is preserved, since key order matters because deserialization
    # has to see the file in the same order it was serialized in so that
    # serializeOnce works correctly.
    log_output = []
    try:
        import json
        from collections import OrderedDict
        data = json.loads(
            request.FILES["value"].read().decode("utf8", "replace"),
            object_pairs_hook=OrderedDict)

        # Update project data.
        project.import_json(data, request.user, lambda x : log_output.append(x))
    except Exception as e:
        log_output.append(str(e))

    # Show an unfriendly response containing log output.
    return JsonResponse(log_output, safe=False, json_dumps_params={"indent": 2})

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
        from_project = Project.objects.filter(id=request.POST["project"], organization=request.organization, members__user=request.user).first()

        # Authorization for adding invitee to the project team.
        if not from_project:
            into_project = False
        else:
            inv_ctx = Invitation.form_context_dict(request.user, from_project, [])
            into_project = (request.POST.get("add_to_team", "") != "") and inv_ctx["can_add_invitee_to_team"]

        # Target.
        if request.POST.get("into_new_task_question_id"):
            # validate the question ID
            target = from_project
            target_info = {
                "into_new_task_question_id": from_project.root_task.module.questions.filter(id=request.POST.get("into_new_task_question_id")).get().id,
            }

        elif request.POST.get("into_task_editorship"):
            target = Task.objects.get(id=request.POST["into_task_editorship"], project__organization=request.organization)
            if not target.has_write_priv(request.user):
                return HttpResponseForbidden()
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
            target = get_object_or_404(Discussion, id=request.POST["into_discussion"], organization=request.organization)
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
            organization=request.organization,

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
    inv = get_object_or_404(Invitation, id=request.POST['id'], organization=request.organization, from_user=request.user)
    inv.revoked_at = timezone.now()
    inv.save(update_fields=['revoked_at'])
    return JsonResponse({ "status": "ok" })

def accept_invitation(request, code=None):
    # This route is handled specially by the siteapp.middleware.OrganizationSubdomainMiddleware that
    # guards access to the subdomain. The user may not be authenticated and may not be a member
    # of the Organization whose subdomain they are visiting.

    assert code.strip() != ""
    inv = get_object_or_404(Invitation, organization=request.organization, email_invitation_code=code)

    response = accept_invitation_do_accept(request, inv)
    if isinstance(response, HttpResponse):
        return response

    # The invitation has been accepted by a logged in user.

    # Some invitations create an interstitial before redirecting.
    inv.from_user.localize_to_org(request.organization)
    try:
        interstitial = inv.target.get_invitation_interstitial(inv)
    except AttributeError: # inv.target may not have get_invitation_interstitial method
        interstitial = None
    if interstitial:
        # If the target provides interstitial context data...
        context = {
            "title": "Accept Invitation to " + inv.purpose(),
            "breadcrumbs_links": [],
            "breadcrumbs_last": "Accept Invitation",
            "continue_url": inv.get_redirect_url(),
        }
        context.update(interstitial)
        return render(request, "interstitial.html", context)

    return HttpResponseRedirect(inv.get_redirect_url())


def accept_invitation_do_accept(request, inv):
    from django.contrib.auth import authenticate, login, logout
    from django.contrib import messages
    from django.http import HttpResponseRedirect
    import urllib.parse

    # Can't accept if this object has expired. Warn the user but
    # send them to the homepage.
    if inv.is_expired():
        messages.add_message(request, messages.ERROR, 'The invitation you wanted to accept has expired.')
        return HttpResponseRedirect("/")

    # Get the user logged into an account.
    
    matched_user = None # inv.to_user \
       # or User.objects.filter(email=inv.to_email).exclude(id=inv.from_user.id).first()
    
    if request.user.is_authenticated() and request.GET.get("accept-auth") == "1":
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
        # User account (if it did, we would have logged the user in immediately because
        # they just confirmed ownership of the address). Ask the user to log in or sign up,
        # redirecting back to this page after with "auth=1" so that we skip the matched
        # user check and accept whatever account the user just logged into or created.
        #
        # In the event the user was already logged into an account that didn't match the
        # invitation email address, log them out now.
        from urllib.parse import urlencode
        logout(request)
        inv.from_user.localize_to_org(request.organization)
        return render(request, "invitation.html", {
            "inv": inv,
            "next": urlencode({ "next": request.path + "?accept-auth=1", }),
        })

    # The user is now logged in and able to accept the invitation.

    # If the invitation was already accepted, then there's nothing more to do.
    if inv.accepted_at:
        return

    # Accept the invitation.
    with transaction.atomic():

        inv.accepted_at = timezone.now()
        inv.accepted_user = request.user

        def add_message(message):
            messages.add_message(request, messages.INFO, message)

        # Add user to a project team.
        if inv.into_project:
            ProjectMembership.objects.get_or_create( # is unique, so test first
                project=inv.from_project,
                user=request.user,
                )
            add_message('You have joined the team %s.' % inv.from_project.title)

        # Run the target's invitation accept function.
        inv.target.accept_invitation(inv, add_message)

        # Update this invitation.
        inv.save()

        # Issue a notification - first to the user who sent the invitation.
        issue_notification(
            request.user,
            "accepted your invitation " + inv.purpose_verb(),
            inv.target,
            recipients=[inv.from_user])

        # - then to other watchers of the target objects (excluding the
        # user who sent the invitation and the user who accepted it).
        issue_notification(
            request.user,
            inv.target.get_invitation_verb_past(inv),
            inv.target,
            recipients=[u for u in inv.target.get_notification_watchers()
                if u not in (inv.from_user, inv.accepted_user)])

