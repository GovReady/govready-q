from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import User, Project, Invitation
from guidedmodules.models import Module, Task, ProjectMembership
from discussion.models import Discussion

from .good_settings_helpers import AllauthAccountAdapter # ensure monkey-patch is loaded
from .notifications_helpers import *

def homepage(request):
    return render(request, "index.html", {
        "has_projects": len(get_user_projects(request)) > 0,
    })

def get_user_projects(request):
    # Show user what they can do --- list the projects they
    # are involved with.
    projects = set()

    # Add all of the Projects the user is a member of within the Organization
    # that the user is on the subdomain of.
    for pm in ProjectMembership.objects\
        .filter(project__organization=request.organization, user=request.user)\
        .select_related('project'):
        projects.add(pm.project)
        if pm.is_admin:
            # Annotate with whether the user is an admin of the project.
            pm.project.user_is_admin = True

    # Add projects that the user is the editor of a task in, even if
    # the user isn't a team member of that project.
    for task in Task.get_all_tasks_readable_by(request.user, request.organization)\
        .order_by('-created')\
        .select_related('project'):
        projects.add(task.project)

    # Add projects that the user is participating in a Discussion in
    # as a guest.
    for d in Discussion.objects.filter(organization=request.organization, guests=request.user):
        if d.attached_to is not None: # because it is generic there is no cascaded delete and the Discussion can become dangling
            projects.add(d.attached_to.task.project)

    # Don't show system projects. They're displayed separately.
    system_projects = set(p for p in projects if p.is_organization_project or p.is_account_project)
    projects -= system_projects

    # Sort.
    projects = sorted(projects, key = lambda x : x.updated, reverse=True)

    return projects

def project_list(request):
    projects = get_user_projects(request)
    for p in projects:
        p.open_tasks = p.get_open_tasks(request.user) # for the template
    return render(request, "project_list.html", {
        "projects": projects,
        "any_have_members_besides_me": ProjectMembership.objects.filter(project__in=projects).exclude(user=request.user),
    })

@login_required
def new_project(request):
    from django.forms import ModelForm, ChoiceField, RadioSelect, MultipleChoiceField, \
        CheckboxSelectMultiple, CharField, Textarea
    from django.core.exceptions import ValidationError

    # Get the list of project modules that this user has access to.
    # The built-in server-side form validation will ensure that the user can
    # only choose one of these at POST.
    project_modules = sorted(set(
        (m.id, m.title)
        for m in Module.objects.filter(visible=True)
        if m.is_startable_project_by(request.user, request.organization)),
        key = lambda m : m[1])

    # Get the list of users who can be invited to the new project.
    invitable_users = (
        User.objects
            # members of this organization
            .filter(projectmembership__project__organization=request.organization)
            # distinct because the field ^ creates duplicates
            .distinct()
            # but not the user making this request
            .exclude(id=request.user.id)
        )

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
            fields = ['title']
            labels = {
                'title': 'Enter name of project or system'
            }
            help_texts = {
                'title': 'Give your web property, application or other IT system a descriptive name.',
            }
        module_id = ChoiceField(choices=project_modules, label="What do you need to do?", widget=RadioSelect)
        if len(invitable_users) > 0:
            invite_org_users = MultipleChoiceField(label='Select existing users to add to project',
                choices=sorted([
                    (user.id, user.render_context_dict(request.organization)['name'])
                    for user in invitable_users ],
                    key = lambda choice : choice[1]),
                widget=CheckboxSelectMultiple,
                required=False)
        invite_by_email = CharField(label="Invite others to this project",
            help_text="Separate email addresses by new lines, spaces, or commas.",
            widget=Textarea(attrs={'rows': '2', 'placeholder': ''}),
            required=False,
            validators=[validate_list_of_email_addresses])

    form = NewProjectForm()
    if request.method == "POST":
        # Save and then go back to the home page to see it.
        form = NewProjectForm(request.POST)
        if not form.errors:
            with transaction.atomic():
                # create object
                project = form.save(commit=False)
                project.organization = request.organization
                project.save()

                # assign root task module from the given module_id
                try:
                    project.set_root_task(int(form.cleaned_data["module_id"]), request.user)
                except ValueError as e:
                    # module_id is invalid or doesn't refer to a project-type module
                    return HttpResponseForbidden(str(e))

                # add user as an admin
                ProjectMembership.objects.create(
                    project=project,
                    user=request.user,
                    is_admin=True)

                # add other invited users
                # (the form field is absent in some cases so must check we have the field)
                if 'invite_org_users' in form.cleaned_data:
                    for user in invitable_users.filter(id__in=form.cleaned_data['invite_org_users']):
                        ProjectMembership.objects.create(
                            project=project,
                            user=user)

                # send other invitations
                for email in validate_list_of_email_addresses(form.cleaned_data['invite_by_email']):
                    inv = Invitation.objects.create(
                        organization=request.organization,
                        from_user=request.user, # sender
                        from_project=project, # sender
                        into_project=True, # action
                        target=project, # action
                        target_info={ "what": "join-team" }, # action
                        to_email=email, # recipient
                        text=""
                    )
                    inv.send()

            return HttpResponseRedirect(project.get_absolute_url() + "/start")

    return render(request, "new-project.html", {
        "first": not ProjectMembership.objects.filter(user=request.user).exists(),
        "form": form,
    })

@login_required
def begin_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, organization=request.organization)
    if project.root_task.module.spec.get("interstitial"):
        return render(request, "interstitial.html", {
            "title": "Starting " + project.title,
            "body": project.root_task.render_field("interstitial"),
            "breadcrumbs_links": [{ "link": project.get_absolute_url(), "title": project.title }],
            "breadcrumbs_last": "Start",
            "next": project.get_absolute_url(),
            "next_text": "I\u2019m Ready",
        })
    else:
        return HttpResponseRedirect(project.get_absolute_url())

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

    # Get the project team members.
    project_members = ProjectMembership.objects.filter(project=project)
    is_project_member = project_members.filter(user=request.user).exists()

    # Get all of the discussions I'm participating in as a guest in this project.
    # Meaning, I'm not a member, but I still need access to certain tasks and
    # certain questions within those tasks.
    discussions = list(project.get_discussions_in_project_as_guest(request.user))

    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    root_task_answers = project.root_task.get_answers()
    root_task_answers = root_task_answers.with_extended_info()

    # Create all of the module entries in a tabs & groups data structure.
    from collections import OrderedDict
    tabs = OrderedDict()
    action_buttons = []
    question_dict = { }
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
                tasks.append(task)
                task.has_write_priv = task.has_write_priv(request.user)
                task_discussions.extend([d for d in discussions if d.attached_to.task == task])
                task.is_finished = task.is_finished() # cache because the template will also use it
                if not task.is_finished:
                    # If any task is unfinished, the whole question
                    # is marked as unfinished.
                    is_finished = False
                elif is_finished is None:
                    # If all tasks are finished, the whole question
                    # is marked as finished.
                    is_finished = True

        # Do not display if user should not be able to see this task.
        if not is_project_member and len(task_discussions) == 0:
            continue

        # Create template context dict.
        d = {
            "question": mq,
            "module": mq.answer_type_module,
            "is_finished": is_finished,
            "tasks": tasks,
            "can_start_new_task": mq.spec["type"] == "module-set" or len(tasks) == 0,
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
                if not t.is_finished:
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
        "is_member": is_project_member,
        "can_begin_module": project.can_start_task(request.user),
        "project_has_members_besides_me": project and project.members.exclude(user=request.user),
        "project": project,
        "title": project.title,
        "intro" : project.root_task.render_field('introduction') if project.root_task.module.spec.get("introduction") else "",
        "additional_tabs": additional_tabs,
        "open_invitations": other_open_invitations,
        "send_invitation": Invitation.form_context_dict(request.user, project, [request.user]),
        "project_members": sorted(project_members, key = lambda mbr : (not mbr.is_admin, str(mbr.user))),
        "tabs": list(tabs.values()),
        "action_buttons": action_buttons,
    })

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

        return HttpResponseRedirect(inv.get_redirect_url())
