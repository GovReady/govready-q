import random
from django.db import IntegrityError
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import ModelForm
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotAllowed, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_perms_for_model

from controls.forms import ImportProjectForm
from discussion.models import Discussion
from guidedmodules.models import (Module, ModuleQuestion, ProjectMembership,
                                  Task)
from controls.models import Element, System

from .forms import PortfolioForm, ProjectForm
from .good_settings_helpers import \
    AllauthAccountAdapter  # ensure monkey-patch is loaded
from .models import Folder, Invitation, Portfolio, Project, User, Organization, Support
from .notifications_helpers import *

import sys
import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()
# logger = logging.getLogger(__name__)


def homepage(request):
    # If the user is logged in, then redirect them to the projects page.
    if request.user.is_authenticated:
        return HttpResponseRedirect("/projects")

    from .views_landing import homepage
    return homepage(request)

def debug(request):
    # Raise Exception to see session information
    raise Exception()
    if request.user.is_authenticated:
        return HttpResponseRedirect("/projects")

    from .views_landing import homepage
    return homepage(request)

def assign_project_lifecycle_stage(projects):
    # Define lifecycle stages.
    # Because we alter this data structure in project_list,
    # we need a new instance of it on every page load.
    lifecycle_stages = [
        {
            "id": "none",
            "label": "Projects",
            "stage_col_width": { "xs-12" }, # "col_" + this => Bootstrap 3 column class
            "stages": [
                { "id": "none", "label": "", "subhead": "" },
            ]
        },
        {
            "id": "us_nist_rmf",
            "label": "NIST Risk Management Framework",
            "stage_col_width": { "md-2" }, # "col_" + this => Bootstrap 3 column class
            "stages": [
                { "id": "1_categorize", "label": "1. Categorize", "subhead": "Information System" },
                { "id": "2_select", "label": "2. Select", "subhead": "Security Controls" },
                { "id": "3_implement", "label": "3. Implement", "subhead": "Security Controls" },
                { "id": "4_assess", "label": "4. Assess", "subhead": "Security Controls" },
                { "id": "5_authorize", "label": "5. Authorize", "subhead": "Information System" },
                { "id": "6_monitor", "label": "6. Monitor", "subhead": "Security Controls" },
            ]
        }
    ]

    # Create a mapping from concatenated lifecycle+stage IDs
    # to tuples of (lifecycle object, stage object).
    lifecycle_stage_code_mapping = { }
    for lifecycle in lifecycle_stages:
        for stage in lifecycle["stages"]:
            lifecycle_stage_code_mapping[lifecycle["id"] + "_" + stage["id"]] = (
                lifecycle,
                stage
            )

    # Load each project's lifecycle stage, which is computed by each project's
    # root task's app's output document named govready_lifecycle_stage_code.
    # That output document yields a string identifying a lifecycle stage.
    for project in projects:
        outputs = project.root_task.render_output_documents()
        for doc in outputs:
            if doc.get("id") == "govready_lifecycle_stage_code":
                value = doc["text"].strip()
                if value in lifecycle_stage_code_mapping:
                    project.lifecycle_stage = lifecycle_stage_code_mapping[value]
                    break
        else:
            # No matching output document with a non-empty value.
            project.lifecycle_stage = lifecycle_stage_code_mapping["none_none"]

def project_list(request):
    # Get all of the projects that the user can see *and* that are in a folder,
    # which indicates it is top-level.
    projects = Project.get_projects_with_read_priv(
        request.user,
        excludes={ "contained_in_folders": None })

    # Sort the projects by their creation date. The projects
    # won't always appear in that order, but it will determine
    # the overall order of the page in a stable way.
    projects = sorted(projects, key = lambda project : project.created)

    # Load each project's lifecycle stage, which is computed by each project's
    # root task's app's output document named govready_lifecycle_stage_code.
    # That output document yields a string identifying a lifecycle stage.
    assign_project_lifecycle_stage(projects)

    # Group projects into lifecyle types, and then lifecycle stages. The lifecycle
    # types are arranged in the order they first appear across the projects.
    lifecycles = []
    for project in projects:
        # On the first occurrence of this lifecycle type, add it to the output.
        if project.lifecycle_stage[0] not in lifecycles:
            lifecycles.append(project.lifecycle_stage[0])

        # Put the project into the lifecycle's appropriate stage.
        project.lifecycle_stage[1].setdefault("projects", []).append(project)

    # Log listing
    logger.info(
        event="project_list",
        user={"id": request.user.id, "username": request.user.username}
    )

    return render(request, "projects.html", {
        "lifecycles": lifecycles,
        "projects": projects,
        "project_form": ProjectForm(request.user),
    })

def project_list_lifecycle(request):
    # Get all of the projects that the user can see *and* that are in a folder,
    # which indicates it is top-level.
    projects = Project.get_projects_with_read_priv(
        request.user,
        excludes={ "contained_in_folders": None })

    # Sort the projects by their creation date. The projects
    # won't always appear in that order, but it will determine
    # the overall order of the page in a stable way.
    projects = sorted(projects, key = lambda project : project.created)

    # Load each project's lifecycle stage, which is computed by each project's
    # root task's app's output document named govready_lifecycle_stage_code.
    # That output document yields a string identifying a lifecycle stage.
    assign_project_lifecycle_stage(projects)

    # Group projects into lifecyle types, and then lifecycle stages. The lifecycle
    # types are arranged in the order they first appear across the projects.
    lifecycles = []
    for project in projects:
        # On the first occurrence of this lifecycle type, add it to the output.
        if project.lifecycle_stage[0] not in lifecycles:
            lifecycles.append(project.lifecycle_stage[0])

        # Put the project into the lifecycle's appropriate stage.
        project.lifecycle_stage[1].setdefault("projects", []).append(project)

    return render(request, "projects_lifecycle_original.html", {
        "lifecycles": lifecycles,
        "projects": projects,
        "project_form": ProjectForm(request.user),
    })

def get_compliance_apps_catalog_for_user(user):
    # Each organization that the user is in sees a different set of compliance
    # apps. Since a user may be a member of multiple organizations, merge the
    # catalogs across all of the organizations they are a member of, but
    # remember which organizations generated which apps.
    from siteapp.models import Organization
    catalog = { }
    for org in Organization.get_all_readable_by(user):
        apps = get_compliance_apps_catalog(org, user.id)
        for app in apps:
            # Add to merged catalog.
            catalog.setdefault(app['key'], app)

            # Merge organization list.
            catalog[app["key"]]["organizations"].add(org)

    # Turn the organization sets into a list because the templates use |first.
    catalog = catalog.values()
    for app in catalog:
        app["organizations"] = sorted(app["organizations"], key = lambda org : org.name)

    return catalog

def get_compliance_apps_catalog(organization, userid):
    # Load the compliance apps available to the given organization.

    from guidedmodules.models import AppVersion
    from collections import defaultdict

    appvers = AppVersion.get_startable_apps(organization, userid)

    # Group the AppVersions into apps. An app is a unique source+appname pair.
    # For each app, one or more versions may be available.
    apps = defaultdict(lambda : [])
    for av in appvers:
        apps[(av.source, av.appname)].append(av)

    # Replace each app entry with a list of AppVersions sorted by reverse database
    # row created date (since we don't necessarily have sortable version numbers).
    apps = [
        sorted(appvers, key = lambda av : av.created, reverse=True)
        for appvers in apps.values()
    ]

    # Collect catalog display metadata for each app from the most recent version
    # of each app.
    apps = [
        render_app_catalog_entry(appvers[0], appvers, organization)
        for appvers in apps
    ]

    return apps

def render_app_catalog_entry(appversion, appversions, organization):
    from guidedmodules.module_logic import render_content
    from guidedmodules.models import image_to_dataurl

    key = "{source}/{name}".format(source=appversion.source.slug, name=appversion.appname)

    catalog = appversion.catalog_metadata
    if not isinstance(catalog, dict): catalog = { }

    app_module = appversion.modules.filter(module_name="app").first()

    return {
        # app identification
        "appsource_id": appversion.source.id,
        "key": key,

        # main display fields
        "title": catalog.get('title') or appversion.appname,
        "description": { # rendered as markdown
            "short": render_content(
                {
                    "template": catalog.get("description", {}).get("short") or "",
                    "format": "markdown",
                },
                None,
                "html",
                "%s %s" % (key, "short description")
            ),
            "long": render_content(
                {
                    "template": catalog.get("description", {}).get("long")
                        or catalog.get("description", {}).get("short")
                        or "",
                    "format": "markdown",
                },
                None,
                "html",
                "%s %s" % (key, "short description")
            )
        },

        # catalog page metadata
        "categories": catalog.get("categories", [catalog.get("category")]),
        "search_haystak": "".join([ # free text search uses this
            appversion.appname,
            catalog.get('title', ""),
            catalog.get("vendor", ""),
            catalog.get("description", {}).get("short", ""),
            catalog.get("description", {}).get("long", ""),
        ]),
        "icon": None if "icon" not in catalog
                    else image_to_dataurl(appversion.get_asset(catalog["icon"]), 128),
        "protocol": app_module.spec.get("protocol", []) if app_module else [],
        
        # catalog detail page metadata
        "vendor": catalog.get("vendor"),
        "vendor_url": catalog.get("vendor_url"),
        "source_url": catalog.get("source_url"),
        "status": catalog.get("status"),
        "version": appversion.version_number,
        "recommended_for": catalog.get("recommended_for", []),

        # versions that can be started
        "versions": appversions,

        # organizations that can launch this app
        "organizations": { organization },

        # placeholder for future logic
        "authz": "none",
    }

def get_task_question(request):
    # Filter catalog by apps that satisfy the right protocol.
    # Get the task and question referred to by the filter.
    try:
        task_id, question_key = request.GET["q"].split("/", 1)
        task = get_object_or_404(Task, id=task_id)
        q = task.module.questions.get(key=question_key)
    except (IndexError, ValueError):
        raise Http404()
    return (task, q)

def app_satifies_interface(app, filter_protocols):
    if isinstance(filter_protocols, ModuleQuestion):
        # Does this question specify a protocol? It must specify a list of protocols.
        question = filter_protocols
        if not isinstance(question.spec.get("protocol"), list):
            raise ValueError("Question {} does not expect a protocol.".format(question))
        filter_protocols = set(question.spec["protocol"])
    elif isinstance(filter_protocols, (list, set)):
        # A list or set of protocol IDs is passed. Turn it into a set if it isn't already.
        filter_protocols = set(filter_protocols)
    else:
        raise ValueError(filter_protocols)

    # Check that every protocol required by the question is implemented by the
    # app.
    return filter_protocols <= set(app["protocol"])

def filter_app_catalog(catalog, request):
    filter_description = None

    if request.GET.get("q"):
        # Check if the app satisfies the interface required by a paricular question.
        # The "q" query string argument is a Task ID plus a ModuleQuestion key.
        # It must be a module-type question with a protocol filter. Only apps that
        # satisfy that protocol are shown.
        task, q = get_task_question(request)
        catalog = filter(lambda app : app_satifies_interface(app, q), catalog)
        filter_description = q.spec["title"]

    if request.GET.get("protocol"):
        # Check if the app satisfies the app protocol interface given.
        catalog = filter(lambda app : app_satifies_interface(app, request.GET["protocol"].split(",")), catalog)
        filter_description = None # can't generate nice description of this filter

    return catalog, filter_description

@login_required
def apps_catalog(request):
    # We use the querystring to remember which question the user is selecting
    # an app to answer, when starting an app from within a project.
    from urllib.parse import urlencode
    forward_qsargs = { }
    if "q" in request.GET: forward_qsargs["q"] = request.GET["q"]

    # Add the portfolio id the user is creating the project from to the args
    if "portfolio" not in request.GET:
        messages.add_message(request, messages.ERROR, "Please select 'Start a project' to continue.")
        return redirect('projects')
    else:
        forward_qsargs["portfolio"] = request.GET["portfolio"]

    # Get the app catalog. If the user is answering a question, then filter to
    # just the apps that can answer that question.
    catalog, filter_description = filter_app_catalog(get_compliance_apps_catalog_for_user(request.user), request)

    # Group by category from catalog metadata.
    from collections import defaultdict
    catalog_by_category = defaultdict(lambda : { "title": None, "apps": [] })
    for app in catalog:
        source_slug, _ = app["key"].split('/')
        app['source_slug'] = source_slug
        for category in app["categories"]:
            catalog_by_category[category]["title"] = (category or "Uncategorized")
            catalog_by_category[category]["apps"].append(app)

    # Sort categories by title and discard keys.
    catalog_by_category = sorted(catalog_by_category.values(), key = lambda category : (
        category["title"] != "Great starter apps", # this category goes first
        category["title"].lower(), # sort case insensitively
        category["title"], # except if two categories differ only in case, sort case-sensitively
        ))

    # Sort the apps within each category.
    for category in catalog_by_category:
        category["apps"].sort(key = lambda app : (
            app["title"].lower(), # sort case-insensitively
            app["title"], # except if two apps differ only in case, sort case-sensitively
        ))

    # If user is superuser, enable creating new apps
    authoring_tool_enabled = request.user.has_perm('guidedmodules.change_module')

    return render(request, "app-store.html", {
        "apps": catalog_by_category,
        "filter_description": filter_description,
        "forward_qsargs": ("?" + urlencode(forward_qsargs)) if forward_qsargs else "",
        "authoring_tool_enabled": authoring_tool_enabled,
        "project_form": ProjectForm(request.user),
    })

@login_required
def apps_catalog_item(request, source_slug, app_name):
    # Is this a module the user has access to? The app store
    # does some authz based on the organization.
    from guidedmodules.models import AppSource
    catalog, _ = filter_app_catalog(get_compliance_apps_catalog_for_user(request.user), request)
    for app_catalog_info in catalog:
        if app_catalog_info["key"] == source_slug + "/" + app_name:
            # We found it.
            break
    else:
        raise Http404()

    # Get portfolio project should be included in.
    if request.GET.get("portfolio"):
      portfolio = Portfolio.objects.get(id=request.GET.get("portfolio"))
    else:
      portfolio = None

    error = None

    if request.method == "POST":
        # Start the app.

        # Get the organization context to start it within.
        for organization in app_catalog_info["organizations"]:
            if organization.slug == request.POST.get("organization"):
                break # found it
        else:
            # Did not find a match.
            raise ValueError("Organization does not permit starting this app.")

        if not request.GET.get("q"):
            # Since we no longer ask what folder to put the new Project into,
            # create a default Folder instance for all started apps that aren't
            # answers to questions. All top-level apps must be in a folder. That's
            # how we know to display it in the project_list view.
            default_folder_name = "Started Apps"
            folder = Folder.objects.filter(
                organization=organization,
                admin_users=request.user,
                title=default_folder_name,
            ).first()
            if not folder:
                folder = Folder.objects.create(organization=organization, title=default_folder_name)
                folder.admin_users.add(request.user)

            # This app is going into a folder. It does not answer a task question.
            task, q = (None, None)
        else:
            # This app is going to answer a question.
            # Don't put it into a folder.
            folder = None

            # It will answer a task. Validate that we're starting an app that
            # can answer that question.
            task, q = get_task_question(request)
            if not app_satifies_interface(app_catalog_info, q):
                raise ValueError("Invalid protocol.")

        # Get portfolio project should be included in.
        if request.GET.get("portfolio"):
          portfolio = Portfolio.objects.get(id=request.GET.get("portfolio"))
        else:
          portfolio = None

        # Start the most recent version of the app.
        appver = app_catalog_info["versions"][0]

        # Start the app.
        from guidedmodules.app_loading import ModuleDefinitionError
        try:
            project = start_app(appver, organization, request.user, folder, task, q, portfolio)
        except ModuleDefinitionError as e:
            error = str(e)
        else:
            if task and q:
                # Redirect to the task containing the question that was just answered.
                from urllib.parse import urlencode
                return HttpResponseRedirect(task.get_absolute_url() + "#" + urlencode({ "q": q.key, "t": project.root_task.id }))

            # Redirect to the new project.
            return HttpResponseRedirect(project.get_absolute_url())

    # Show the "app" page.
    return render(request, "app-store-item.html", {
        "app": app_catalog_info,
        "error": error,
        "project_form": ProjectForm(request.user),
        "source_slug": source_slug,
        "portfolio": portfolio
    })

def start_app(appver, organization, user, folder, task, q, portfolio):
    from guidedmodules.app_loading import load_app_into_database

    # Begin a transaction to create the Module and Task instances for the app.
    with transaction.atomic():
        # Create project.
        project = Project()
        project.organization = organization
        project.portfolio = portfolio

        # Save and add to folder
        project.save()
        project.set_root_task(appver.modules.get(module_name="app"), user)
        # Update default name to be unique by using project.id
        project.root_task.title_override = project.title + " " + str(project.id)
        project.root_task.save()
        if folder:
            folder.projects.add(project)

        # Log start app / new project
        logger.info(
            event="start_app",
            object={"task": "project", "id": project.root_task.id, "title": project.root_task.title_override},
            user={"id": user.id, "username": user.username}
        )
        logger.info(
            event="new_project",
            object={"object": "project", "id": project.id, "title":project.title},
            user={"id": user.id, "username": user.username}
        )

        # Create a new System element and link to project?
        # Top level apps should be linked to a system
        # Create element to serve as system's root_element
        # Element names must be unique. Use unique project title set above.
        element = Element()
        element.name = project.title
        element.element_type = "system"
        element.save()
        # Create system
        system = System(root_element=element)
        system.save()
        # Link system to project
        project.system = system
        project.save()
        # Log start app / new project
        logger.info(
            event="new_element new_system",
            object={"object": "element", "id": element.id, "name":element.name},
            user={"id": user.id, "username": user.username}
        )

        # Add user as the first admin.
        ProjectMembership.objects.create(
            project=project,
            user=user,
            is_admin=True)
        # Grant owner permissions on root_element to user
        element.assign_owner_permissions(user)
        # Log ownership assignment
        logger.info(
                event="new_element new_system assign_owner_permissions",
                object={"object": "element", "id": element.id, "name":element.name},
                user={"id": user.id, "username": user.username}
            )
        system.assign_owner_permissions(user)
        # Log ownership assignment
        logger.info(
                event="new_system assign_owner_permissions",
                object={"object": "system", "id": system.root_element.id, "name":system.root_element.name},
                user={"id": user.id, "username": user.username}
            )

        if task and q:
            # It will also answer a task's question.
            ans, is_new = task.answers.get_or_create(question=q)
            ansh = ans.get_current_answer()
            if q.spec["type"] == "module" and ansh and ansh.answered_by_task.count():
                raise ValueError('The question %s already has an app associated with it.'
                    % q.spec["title"])
            ans.save_answer(
                None, # not used for module-type questions
                list([] if not ansh else ansh.answered_by_task.all()) + [project.root_task],
                None,
                user,
                "web")

        return project

def project_read_required(f):
    @login_required
    def g(request, project_id, project_url_suffix):
        project = get_object_or_404(Project, id=project_id)

        # Check authorization.
        has_project_portfolio_permissions = request.user.has_perm('view_portfolio', project.portfolio)
        if not project.has_read_priv(request.user) and not has_project_portfolio_permissions:
            return HttpResponseForbidden()

        # Redirect if slug is not canonical. We do this after checking for
        # read privs so that we don't reveal the task's slug to unpriv'd users.
        if request.path != project.get_absolute_url()+project_url_suffix:
            return HttpResponseRedirect(project.get_absolute_url())

        return f(request, project)
    return g

@project_read_required
def project(request, project):

    # Get this project's lifecycle stage, which is shown below the project title.
    assign_project_lifecycle_stage([project])
    if project.lifecycle_stage[0]["id"] == "none":
        # Kill it if it's the default lifecycle.
        project.lifecycle_stage = None
    else:
        # Mark the stages up to the active one as completed.
        for stage in project.lifecycle_stage[0]["stages"]:
            stage["complete"] = True
            if stage == project.lifecycle_stage[1]:
                break

    # Get all of the discussions the user is participating in as a guest in this project.
    # Meaning, I'm not a member, but I still need access to certain tasks and
    # certain questions within those tasks.
    discussions = list(project.get_discussions_in_project_as_guest(request.user))

    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    root_task_answers = project.root_task.get_answers().with_extended_info()

    # Check if this user has authorization to start tasks in this Project.
    can_start_task = project.can_start_task(request.user)

    # Collect all of the questions and answers, i.e. the sub-tasks, that we'll display.
    # Create a "question" record for each question that is displayed by the template.
    # For module-set questions, create one record to start new entries and separate
    # records for each answered module.
    from collections import OrderedDict
    questions = OrderedDict()
    can_start_any_apps = False
    for (mq, is_answered, answer_obj, answer_value) in root_task_answers.answertuples.values():
        # Display module/module-set questions only. Other question types in a project
        # module are not valid.
        if mq.spec.get("type") not in ("module", "module-set"):
            continue

        # Skip questions that are imputed.
        if is_answered and not answer_obj:
            continue

        # Create a "question" record for all Task answers to this question.
        if answer_value is None:
            # Question is unanswered - there are no sub-tasks.
            answer_value = []
        elif mq.spec["type"] == "module":
            # The answer is a ModuleAnswers instance. Wrap it in an array containing
            # just itself so we create as single question entry.
            answer_value = [answer_value]
        elif mq.spec["type"] == "module-set":
            # The answer is already a list of zero-or-more ModuleAnswers instances.
            pass

        # If the question specification specifies an icon asset, load the asset.
        # This saves the browser a request to fetch it, which is somewhat
        # expensive because assets are behind authorization logic.
        if "icon" in mq.spec:
            icon = project.root_task.get_static_asset_image_data_url(mq.spec["icon"], 75)
        else:
            icon = None

        for i, module_answers in enumerate(answer_value):
            # Create template context dict for this question.
            key = mq.id
            if mq.spec["type"] == "module-set":
                key = (mq.id, i)
            questions[key] = {
                "question": mq,
                "icon": icon,
                "invitations": [], # filled in below
                "task": module_answers.task,
                "can_start_new_task": False,
                "discussions": [d for d in discussions if d.attached_to.task == module_answers.task],
            }

        # Create a "question" record for the question itself it is is unanswered or if
        # this is a module-set question, and only if the user has permission to start tasks.
        if can_start_task and (len(answer_value) == 0 or mq.spec["type"] == "module-set"):
            questions[mq.id] = {
                "question": mq,
                "icon": icon,
                "invitations": [], # filled in below
                "can_start_new_task": True,
            }

            # Set a flag if any app can be started, i.e. if this question has a protocol field.
            # Is this a protocol question?
            if mq.spec.get("protocol"):
                can_start_any_apps = True

    # Assign questions to the main area or to the "action buttons" panel on the side of the page.
    main_area_questions = []
    action_buttons = []
    for q in questions.values():
        mq = q["question"]
        if mq.spec.get("placement") == None:
            main_area_questions.append(q)
        elif mq.spec.get("placement") == "action-buttons":
            action_buttons.append(q)

    # Choose a layout mode. Use the "columns" layout if any question
    # has a 'protocol' field. Otherwise use the "rows" layout.
    layout_mode = "rows"
    for q in main_area_questions:
        if q["question"].spec.get("protocol"):
            layout_mode = "columns"

    # Assign main-area questions to columns. For non-"columns" layouts,
    # assign to one giant column.
    if layout_mode != "columns":
        columns= [{
            "questions": main_area_questions,
        }]
    else:
        # number of columns must divide 12 evenly
        columns = [
            { "title": "To Do" },
            { "title": "In Progress" },
            { "title": "Completed" },
            { "title": "Submitted" },
            { "title": "Under Review" },
            { "title": "Accepted" },
        ]
        for column in columns:
            column["questions"] = []

        for question in main_area_questions:
            if "task" not in question:
                col = 0
                question["hide_icon"] = True
            elif question["task"].is_finished():
                col = 2
            elif question["task"].is_started():
                col = 1
            else:
                col = 1
            columns[col]["questions"].append(question)

    # Assign questions in columns to groups.
    for i, column in enumerate(columns):
        column["groups"] = OrderedDict()
        for q in column["questions"]:
            mq = q["question"]
            groupname = mq.spec.get("group")
            group = column["groups"].setdefault(groupname, {
                "title": groupname,
                "questions": [],
            })
            group["questions"].append(q)
        del column["questions"]
        column["groups"] = list(column["groups"].values())

        #column["has_tasks_on_left"] = ((i > 0) and (columns[i-1]["groups"] or columns[i-1]["has_tasks_on_left"]))

    # Are there any output documents that we can render?
    has_outputs = False
    for doc in project.root_task.module.spec.get("output", []):
        if "id" in doc:
            has_outputs = True

    # Find any open invitations and if they are for particular modules,
    # display them with the module.
    other_open_invitations = []
    for inv in Invitation.objects.filter(from_user=request.user, from_project=project, accepted_at=None, revoked_at=None).order_by('-created'):
        if inv.is_expired():
            continue
        if inv.target == project:
            into_new_task_question_id = inv.target_info.get("into_new_task_question_id")
            if into_new_task_question_id:
                if into_new_task_question_id in questions: # should always be True
                    questions[into_new_task_question_id]["invitations"].append(inv)
                    continue

        # If the invitation didn't get put elsewhere, display in the
        # other list.
        other_open_invitations.append(inv)

    # Render.
    return render(request, "project.html", {
        "is_project_page": True,
        "project": project,

        "is_admin": request.user in project.get_admins(),
        "can_upgrade_app": project.root_task.module.app.has_upgrade_priv(request.user),
        "can_start_task": can_start_task,
        "can_start_any_apps": can_start_any_apps,

        "title": project.title,
        "open_invitations": other_open_invitations,
        "send_invitation": Invitation.form_context_dict(request.user, project, [request.user]),
        "has_outputs": has_outputs,

        "layout_mode": layout_mode,
        "columns": columns,
        "action_buttons": action_buttons,

        "projects": Project.objects.all(),
        "portfolios": Portfolio.objects.all(),
        "users": User.objects.all(),

        "authoring_tool_enabled": project.root_task.module.is_authoring_tool_enabled(request.user),
        "project_form": ProjectForm(request.user, initial={'portfolio': project.portfolio.id}),
        "import_project_form": ImportProjectForm()
    })

@project_read_required
def project_settings(request, project):
    """Display settings for project"""

    # Assign questions to the main area or to the "action buttons" panel on the side of the page.
    main_area_questions = []
    action_buttons = []

    other_open_invitations = []
    for inv in Invitation.objects.filter(from_user=request.user, from_project=project, accepted_at=None, revoked_at=None).order_by('-created'):
        if inv.is_expired():
            continue
        if inv.target == project:
            into_new_task_question_id = inv.target_info.get("into_new_task_question_id")
            if into_new_task_question_id:
                if into_new_task_question_id in questions: # should always be True
                    questions[into_new_task_question_id]["invitations"].append(inv)
                    continue

        # If the invitation didn't get put elsewhere, display in the
        # other list.                
        other_open_invitations.append(inv)

    # Gather version upgrade information
    available_versions = []
    avs = project.available_root_task_versions_for_upgrade
    for av in avs:
        av_info = {
            "appname": av.appname,
            "version_number": av.version_number
        }
        # print("project.is_safe_upgrade(av)", project.is_safe_upgrade(av))
        if project.is_safe_upgrade(av) == True:
            av_info["is_safe_upgrade"] = True
            av_info["reason"] = "Compatible"
        else:
            av_info["is_safe_upgrade"] = "Incompatible"
            av_info["reason"] = project.is_safe_upgrade(av)
        available_versions.append(av_info)

    # Render.
    return render(request, "project_settings.html", {
        "is_project_page": True,
        "project": project,

        "is_admin": request.user in project.get_admins(),
        "can_upgrade_app": project.root_task.module.app.has_upgrade_priv(request.user),
        "available_versions": available_versions,

        "title": project.title,
        "open_invitations": other_open_invitations,
        "send_invitation": Invitation.form_context_dict(request.user, project, [request.user]),

        "action_buttons": action_buttons,

        "projects": Project.objects.all(),
        "portfolios": Portfolio.objects.all(),
        "users": User.objects.all(),

        "project_form": ProjectForm(request.user, initial={'portfolio': project.portfolio.id}),
        "import_project_form": ImportProjectForm()
    })

@project_read_required
def project_list_all_answers(request, project):
    sections = []

    def recursively_find_answers(path, task):
        # Get the answers + imputed answers for the task.
        answers = task.get_answers().with_extended_info()

        # Create row in the output table for the answers.
        section = {
            "task": task,
            "path": path,
            "can_review": task.has_review_priv(request.user),
            "answers": [],
        }
        sections.append(section)

        # Append all of the questions and answers.
        for q, a, value_display in answers.render_answers(show_unanswered=False, show_imputed=False):
            section["answers"].append((q, a, value_display))

        if len(path) == 0:
            path = path + [task.title]

        for q, is_answered, a, value in answers.answertuples.values():
            # Recursively go into submodules.
            if q.spec["type"] in ("module", "module-set"):
                if a and a.answered_by_task.exists():
                    for t in a.answered_by_task.all():
                        recursively_find_answers(path + [q.spec["title"]], t)

    # Start at the root task and compute a table of all answers, recursively.
    recursively_find_answers([], project.root_task)

    from guidedmodules.models import TaskAnswerHistory
    return render(request, "project-list-answers.html", {
        "page_title": "Review Answers",
        "project": project,
        "answers": sections,
        "review_choices": TaskAnswerHistory.REVIEW_CHOICES,
    })

@project_read_required
def project_outputs(request, project):
    # To render fast, combine all of the templates by type and render as
    # a single template. Collate documents by type...
    from collections import defaultdict
    documents_by_format = defaultdict(lambda : [])
    for doc in project.root_task.module.spec.get("output", []):
        if "id" in doc and "format" in doc and "template" in doc:
            documents_by_format[doc["format"]].append(doc)

    # Set in a fixed order.
    documents_by_format = list(documents_by_format.items())

    # Combine documents and render.
    import html
    header = {
        "markdown": lambda anchor, title : (
               "\n\n"
             + ("<a name='%s'></a>" % anchor)
             + "\n\n"
             + "# " + html.escape(title)
             + "\n\n" ),
        "text": lambda anchor, title : (
               "\n\n"
             + title
             + "\n\n" ),
    }
    joiner = {
        "markdown": "\n\n",
        "text": "\n\n",
    }
    toc = []
    combined_output = ""
    for format, docs in documents_by_format:
        # Combine the templates of the documents.
        templates = []
        for doc in docs:
            anchor = "doc_%d" % len(toc)
            title = doc.get("title") or doc["id"]
            # TODO: Can we move the HTML back into the template?
            templates.append(header[format](anchor, title) + "<div class='doc'>"+doc["template"]+"</div>")
            toc.append((anchor, title))
        template = joiner[format].join(templates)

        # Render.
        from guidedmodules.module_logic import render_content
        try:
            content = render_content({
                "format": format,
                "template": template
                },
                project.root_task.get_answers().with_extended_info(),
                "html",
                "project output documents",
                show_answer_metadata=True
                )
        except ValueError as e:
            content = str(e)

        # Combine rendered content that was generated by format.
        combined_output += "<div>" + content + "</div>\n\n"

    return render(request, "project-outputs.html", {
        "can_upgrade_app": project.root_task.module.app.has_upgrade_priv(request.user),
        "authoring_tool_enabled": project.root_task.module.is_authoring_tool_enabled(request.user),
        "page_title": "Related Controls",
        "project": project,
        "toc": toc,
        "combined_output": combined_output,
    })

@project_read_required
def project_api(request, project):
    # Explanatory page for an API for this project.

    # Create sample output.
    sample = project.export_json(include_file_content=False, include_metadata=False)

    # Create sample POST body data by randomly choosing question
    # answers.
    def select_randomly(sample, level=0):
        import collections, random
        if not isinstance(sample, dict): return sample
        if level == 0:
            keys = list(sample)
        else:
            keys = random.sample(list(sample), min(level, len(sample)))
        return collections.OrderedDict([
            (k, select_randomly(v, level=level+1))
            for k, v in sample.items()
            if k in keys and "." not in k
        ])
    sample_post_json = select_randomly(sample)

    # Turn the sample JSON POST into a key-value version.
    def flatten_json(path, node, output):
        if isinstance(node, dict):
            if set(node.keys()) == set(["type", "url", "size"]):
                # This looks like a file field.
                flatten_json(path, "<binary file content>", output)
            else:
                for entry, value in node.items():
                    if "." in entry: continue # a read-only field
                    flatten_json(path+[entry], value, output)
        elif isinstance(node, list):
            for item in node:
                flatten_json(path, item, output)
        else:
            if node is None:
                # Can't convert this to a string - it will be the string "None".
                node = "some value here"
            output.append((".".join(path), str(node).replace("\n", "\\n").replace("\r", "\\r")))
    sample_post_keyvalue = []
    flatten_json(["project"], sample["project"], sample_post_keyvalue)

    # Format sample output.
    def format_sample(sample):
        import json
        from pygments import highlight
        from pygments.lexers import JsonLexer
        from pygments.formatters import HtmlFormatter
        sample = json.dumps(sample, indent=2)
        return highlight(sample, JsonLexer(), HtmlFormatter())

    # Construct a schema.
    schema = []
    def make_schema(path, task, module):
        # Get the questions within this task/module and, if we have a
        # task, get the current answers too.
        if task:
            items = list(task.get_current_answer_records())
        else:
            items = [(q, None) for q in module.questions.order_by('definition_order')]
        
        def add_filter_field(q, suffix, title):
            from guidedmodules.models import ModuleQuestion
            schema.append( (path, module, ModuleQuestion(
                key=q.key+'.'+suffix,
                spec={
                    "type": "text",
                    "title": title + " of " + q.spec["title"] + ". Read-only."
                })))

        # Create row in the output table for the fields.
        for q, a in items:
            if q.spec["type"] == "interstitial": continue
            schema.append( (
                path,
                module,
                q ))

            if q.spec["type"] == "longtext": add_filter_field(q, "html", "HTML rendering")
            if q.spec["type"] == "choice": add_filter_field(q, "html", "Human-readable value")
            if q.spec["type"] == "yesno": add_filter_field(q, "html", "Human-readable value ('Yes' or 'No')")
            if q.spec["type"] == "multiple-choice": add_filter_field(q, "html", "Comma-separated human-readable value")
            if q.spec["type"] == "datagrid": add_filter_field(q, "html", "Array of dictionaries for Datagrid")

        # Document the fields of the sub-modules together.
        for q, a in items:
            if q.spec["type"] in ("module", "module-set"):
                if a and a.answered_by_task.exists():
                    # Follow an instantiated task where possible.
                    t = a.answered_by_task.first()
                    make_schema(path + [q.key], t, t.module)
                elif q.answer_type_module:
                    # Follow a module specified in the module specification.
                    make_schema(path + [q.key], None, q.answer_type_module)

    # Start at the root task and compute a table of fields, recursively.
    make_schema(["project"], project.root_task, project.root_task.module)

    return render(request, "project-api.html", {
        "page_title": "API Documentation",
        "project": project,
        "SITE_ROOT_URL": settings.SITE_ROOT_URL,
        "sample": format_sample(sample),
        "sample_post_keyvalue": sample_post_keyvalue,
        "sample_post_json": format_sample(sample_post_json),
        "schema": schema,
    })

@login_required
def show_api_keys(request):
    # Reset.
    if request.method == "POST" and request.POST.get("method") == "resetkeys":
        request.user.reset_api_keys()

        messages.add_message(request, messages.INFO, 'Your API keys have been reset.')

        return HttpResponseRedirect(request.path)

    api_keys = request.user.get_api_keys()
    return render(request, "api-keys.html", {
        "api_key_ro": api_keys['ro'],
        "api_key_rw": api_keys['rw'],
        "api_key_wo": api_keys['wo'],
    })

@login_required
def new_folder(request):
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    f = Folder.objects.create(
        organization=organization, # TODO
        title=request.POST.get("title") or "New Folder",
    )
    f.admin_users.add(request.user)
    return JsonResponse({ "status": "ok", "id": f.id, "title": f.title })

def project_admin_login_post_required(f):
    # Wrap the function to do authorization and change arguments.
    def g(request, project_id, *args):
        # Get project, check authorization.
        project = get_object_or_404(Project, id=project_id)
        has_owner_project_portfolio_permissions = request.user.has_perm('can_grant_portfolio_owner_permission', project.portfolio)
        if request.user not in project.get_admins() and not has_owner_project_portfolio_permissions:
            return HttpResponseForbidden()

        # Call function with changed argument.
        return f(request, project)

    # Apply the require_http_methods decorator.
    g = require_http_methods(["POST"])(g)

    # Apply the login_required decorator.
    g = login_required(g)

    return g

@project_admin_login_post_required
def rename_project(request, project):
    # Update the project's title, which is actually updating its root_task's title_override.
    # If the title isn't changing, don't store it. If the title is set to empty, clear the
    # override.
    title = request.POST.get("title", "").strip() or None
    project.root_task.title_override = title
    project.root_task.save()
    # Update name of linked System root.element if exists
    if project.system is not None:
        project.system.root_element.name = title
        project.system.root_element.save()
    project.root_task.on_answer_changed()
    return JsonResponse({ "status": "ok" })

def move_project(request, project_id):
    """Move project to a new portfolio
    Args:
    request ([HttpRequest]): The network request
    project_id ([int|str]): The id of the project
    Returns:
        [JsonResponse]: Either a ok status or an error 
    """
    try:
        new_portfolio_id = request.POST.get("new_portfolio", "").strip() or None
        project = get_object_or_404(Project, id=int(project_id))
        cur_portfolio = project.portfolio
        new_portfolio = get_object_or_404(Portfolio, id=int(new_portfolio_id))
        project.portfolio = new_portfolio
        project.save()
        # Log successful project move to a different portfolio
        logger.info(
            event="move_project_different_portfolio successful",
            object={"project_id": project.id,"new_portfolio_id": new_portfolio.id},
            from_portfolio={"portfolio_title": cur_portfolio.title, "id": cur_portfolio.id},
            to_portfolio={"portfolio_title": new_portfolio.title, "id": new_portfolio.id}
        )
        # message = "Project {} successfully moved to portfolio {}".format(project, new_portfolio.title)
        # messages.add_message(request, messages.INFO, message)
        return JsonResponse({ "status": "ok" })
    except:
        # Log unsuccessful project move to a different portfolio
        logger.info(
            event="move_project_different_portfolio successful",
            object={"project_id": project.id,"new_portfolio_id": new_portfolio.id},
            from_portfolio={"portfolio_title": cur_portfolio.title, "id": cur_portfolio.id},
            to_portfolio={"portfolio_title": new_portfolio.title, "id": new_portfolio.id}
        )
        # message = "Project {} failed moved to portfolio {}".format(project, new_portfolio.title)
        # messages.add_message(request, messages.ERROR, message)
        return JsonResponse({ "status": "error", "message": sys.exc_info() })

@project_admin_login_post_required
def upgrade_project(request, project):
    """Upgrade root task of project to newer version"""

    available_versions = project.available_root_task_versions_for_upgrade
    current_app = project.root_task.module.app

    # Determine new version of app to upgrade from version_number
    version_number = request.POST.get("version_number", "").strip() or None
    new_app = None
    for av in available_versions:
        if av.version_number == version_number:
            new_app = av

    # Attempt upgrade
    result = project.upgrade_root_task_app(new_app)
    # Was upgrade successful?
    if result == True:
        # Upgrade successful
        # Log successful project root task upgrade
        logger.info(
            event="upgrade_project root_task successful",
            object={"id": project.id, "title":project.title},
            from_app={"appsource_slug": project.root_task.module.source.slug, "id": new_app.id, "version_number": version_number},
            to_app={"appsource_slug": project.root_task.module.source.slug, "id": new_app.id, "version_number": new_app.version_number},
            user={"id": request.user.id, "username": request.user.username}
        )
        message = "Project {} upgraded successfully to {}".format(project, new_app.version_number)
        messages.add_message(request, messages.INFO, message)
        redirect = project.get_absolute_url()
        return JsonResponse({ "status": "ok", "redirect": redirect })
    else:
        # Upgrade failure
        # Log failed project root task upgrade
        logger.info(
            event="upgrade_project root_task failure",
            object={"id": project.id, "title":project.title},
            from_app={"appsource_slug": project.root_task.module.source.slug, "id": new_app.id, "version_number": version_number},
            to_app={"appsource_slug": project.root_task.module.source.slug, "id": new_app.id, "version_number": new_app.version_number},
            detail={"reason": result},
            user={"id": request.user.id, "username": request.user.username}
        )
        message = "Project {} failed to upgrade to {}. {}".format(project, new_app.version_number, result)
        return JsonResponse({ "status": "error", "message": message })

@project_admin_login_post_required
def delete_project(request, project):
    if not project.is_deletable():
        return JsonResponse({ "status": "error", "message": "This project cannot be deleted." })

    # Get the project's parents for redirect.
    parents = project.get_parent_projects()
    project.delete()

    # Only choose parents the user can see.
    parents = [parent for parent in parents if parent.has_read_priv(request.user)]
    if len(parents) > 0:
        redirect = parents[0].get_absolute_url()
    else:
        redirect = "/"

    return JsonResponse({ "status": "ok", "redirect": redirect })

@project_admin_login_post_required
def make_revoke_project_admin(request, project):
    # Make a user an admin of a project or revoke that privilege.
    mbr = ProjectMembership.objects\
        .filter(
            project=project,
            user__id=request.POST.get("user"))\
        .first()
    if mbr:
        mbr.is_admin = (request.POST.get("is_admin") == "true")
        mbr.save()
    return JsonResponse({ "status": "ok" })

@project_admin_login_post_required
def export_project_questionnaire(request, project):
    from urllib.parse import quote
    data = project.export_json(include_metadata=True, include_file_content=True)
    resp = JsonResponse(data, json_dumps_params={"indent": 2})
    filename = project.title.replace(" ","_") + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M")
    resp["content-disposition"] = "attachment; filename=%s.json" % quote(filename)
    return resp

@project_admin_login_post_required
def import_project_questionnaire(request, project):
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
    except Exception as e:
        log_output.append("There was an error reading the export file.")
    else:
        try:
            # Update project data.
            project.import_json(data, request.user, "imp", lambda x : log_output.append(x))
        except Exception as e:
            log_output.append(str(e))

    return render(request, "project-import-finished.html", {
        "project": project,
        "log": log_output,
        "project_form": ProjectForm(request.user, initial={'portfolio': project.portfolio.id}),
    })

def project_start_apps(request, *args):
    # What questions can be answered with an app?
    def get_questions(project):
        # Load the Compliance Store catalog of apps.
        all_apps = get_compliance_apps_catalog(project.organization)

        # A question can be answered with an app if it is a module or module-set
        # question with a protocol value and the question has not already been
        # answered (inclding imputed).
        root_task_answers = project.root_task.get_answers().with_extended_info().as_dict()
        for q in project.root_task.module.questions.order_by('definition_order'):
            if    q.spec["type"] in ("module", "module-set") \
             and  q.spec.get("protocol") \
             and (q.key not in root_task_answers or q.spec["type"] == "module-set"):
                # What apps can be used to start this question?
                q.startable_apps = list(filter(lambda app : app_satifies_interface(app, q), all_apps))
                if len(q.startable_apps) > 0:
                    yield q

    # Although both pages should require admin access, our admin decorator
    # also checks that the request is a POST. So to simplify, use the GET/READ
    # decorator for GET and the POST/ADMIN decorator for POST.
    if request.method == "GET":
        @project_read_required
        def viewfunc(request, project):
            return render(request, "project-startapps.html", {
                "project": project,
                "questions": list(get_questions(project)),
            })
    else:
        @project_admin_login_post_required
        def viewfunc(request, project):
            # Start all of the indiciated apps. Validate that the
            # chosen app satisfies the protocol. For each app,
            # start the most recent version of the app.
            errored_questions = []
            for q in get_questions(project):
                if q.key in request.POST:
                    startable_apps = { app["key"]: app["versions"][0] for app in q.startable_apps}
                    if request.POST[q.key] in startable_apps:
                        app = startable_apps[request.POST[q.key]]
                        try:
                            start_app(app, project.organization, request.user, None, project.root_task, q)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            errored_questions.append((q, app, e))

            if len(errored_questions) == 0:
                return JsonResponse({ "status": "ok" })
            else:
                message = "There was an error starting the following apps: "
                message += ", ".join(
                    "{app} ({appname}) for {title} ({key}) ({error})".format(
                        app=app["title"],
                        appname=app["key"],
                        title=q.spec["title"],
                        key=q.key,
                        error=error,
                    )
                    for q, app, error in errored_questions
                )
                return JsonResponse({ "status": "error", "message": message })

    return viewfunc(request, *args)

# PORTFOLIOS

def update_permissions(request):
    permission = request.POST.get('permission')
    portfolio_id = request.POST.get('portfolio_id')
    user_id = request.POST.get('user_id')
    portfolio = Portfolio.objects.get(id=portfolio_id)
    user = User.objects.get(id=user_id)
    # TODO check if this check on request.user can be moved to decorator
    if request.user.has_perm('can_grant_portfolio_owner_permission', portfolio):
      if permission == 'remove_permissions':
        portfolio.remove_permissions(user)
      elif permission == 'grant_owner_permission':
        portfolio.assign_owner_permissions(user)
        # Log permission escalation
        logger.info(
            event="update_permissions portfolio assign_owner_permissions",
            object={"id": portfolio.id, "title":portfolio.title},
            receiving_user={"id": user.id, "username": user.username},
            user={"id": request.user.id, "username": request.user.username}
        )
      elif permission == 'remove_owner_permissions':
        portfolio.remove_owner_permissions(user)
        # Log permission removal
        logger.info(
            event="update_permissions portfolio remove_owner_permissions",
            object={"id": portfolio.id, "title":portfolio.title},
            receiving_user={"id": user.id, "username": user.username},
            user={"id": request.user.id, "username": request.user.username}
        )
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

@login_required
def portfolio_list(request):
    """List portfolios"""

    logger.info(
        event="portfolio_list",
        user={"id": request.user.id, "username": request.user.username}
    )

    return render(request, "portfolios/index.html", {
        "portfolios": request.user.portfolio_list() if request.user.is_authenticated else None,
        "project_form": ProjectForm(request.user),
    })

@login_required
def new_portfolio(request):
    """Form to create new portfolios"""
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            form.save()
            portfolio = form.instance
            logger.info(
                event="new_portfolio",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username}
            )
            portfolio.assign_owner_permissions(request.user)
            logger.info(
                event="new_portfolio assign_owner_permissions",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                receiving_user={"id": request.user.id, "username": request.user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            return redirect('portfolio_projects', pk=portfolio.pk)
    else:
        form = PortfolioForm()
    return render(request, 'portfolios/form.html', {
        'form': form,
        "project_form": ProjectForm(request.user),
    })

@login_required
def delete_portfolio(request, pk):
    """Form to delete portfolios"""

    if request.method == 'GET':
        portfolio = Portfolio.objects.get(pk=pk)

        # Confirm user has permission to delete portfolio
        CAN_DELETE_PORTFOLIO = False
        if request.user.is_superuser or request.user.has_perm('delete_portfolio', portfolio):
            CAN_DELETE_PORTFOLIO = True

        if not CAN_DELETE_PORTFOLIO:
            logger.info(
                event="delete_portfolio_failed",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username},
                detail={"message": "USER IS SUPER USER"}
            )
            messages.add_message(request, messages.ERROR, f"You do not have permission to delete portfolio '{portfolio.title}.'")
            return redirect("list_portfolios")

        # Only delete a portfolio with no projects
        if len(portfolio.projects.all()) > 0:
            logger.info(
                event="delete_portfolio_failed",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username},
                detail={"message": "Portfolio not empty"}
            )
            messages.add_message(request, messages.ERROR, f"Failed to delete portfolio '{portfolio.title}.' The portfolio is not empty.")
            return redirect("list_portfolios")
        # TODO: It will delete everything related to the portfolio as well with a summary of the deletion
        # Delete portfolio
        try:
            Portfolio.objects.get(pk=pk).delete()
            logger.info(
                event="delete_portfolio",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username}
            )
            messages.add_message(request, messages.INFO, f"The portfolio '{portfolio.title}' has been deleted.")
            return redirect("list_portfolios")
        except:
            logger.info(
                event="delete_portfolio_failed",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username},
                detail={"message": "Other error when running delete on portfolio object."}
            )

@login_required
def edit_portfolio(request, pk):
    """Form to edit portfolios"""
    portfolio = Portfolio.objects.get(pk=pk)
    form = PortfolioForm(request.POST or None, instance=portfolio, initial={'portfolio': portfolio.id})
    # Confirm user has permission to edit portfolio
    CAN_EDIT_PORTFOLIO = False
    if request.user.is_superuser or request.user.has_perm('change_portfolio', portfolio):
        CAN_EDIT_PORTFOLIO = True
    if request.method == 'GET':
        if not CAN_EDIT_PORTFOLIO:
            logger.info(
                event="delete_portfolio_failed",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username},
                detail={"message": "USER IS SUPER USER"}
            )
            messages.add_message(request, messages.ERROR, f"You do not have permission to delete portfolio '{portfolio.title}.'")
            return redirect("list_portfolios")

        if form.is_valid():
            form.save()

            logger.info(
                event="edit_portfolio",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                user={"id": request.user.id, "username": request.user.username}
            )
            portfolio.assign_owner_permissions(request.user)
            logger.info(
                event="new_portfolio assign_owner_permissions",
                object={"object": "portfolio", "id": portfolio.id, "title": portfolio.title},
                receiving_user={"id": request.user.id, "username": request.user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            return redirect('portfolio_projects', pk=portfolio.pk)
    if request.method == 'POST':
        try:
            form = PortfolioForm(request.POST, instance=portfolio)
            if form.is_valid():
                form.save()
                # Log portfolio update
                messages.add_message(request, messages.INFO, f"The portfolio '{portfolio.title}' has been updated.")
                return redirect("list_portfolios")
        except IntegrityError:
            messages.add_message(request, messages.ERROR, "Portfolio name {} not available.".format(request.POST['title']))

    return render(request, 'portfolios/edit_form.html', {
        'form': form,
        'portfolio': portfolio,
        "can_edit_portfolio": CAN_EDIT_PORTFOLIO,
    })

def portfolio_read_required(f):
    @login_required
    def g(request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk)

        # Check authorization.
        has_portfolio_permissions = request.user.has_perm('view_portfolio', portfolio)
        has_portfolio_project_permissions = False
        projects = Project.objects.filter(portfolio_id=portfolio.id)
        for project in projects:
            if request.user.has_perm('view_project', project):
                has_portfolio_project_permissions = True

        if not (has_portfolio_permissions or has_portfolio_project_permissions):
            return HttpResponseForbidden()
        return f(request, portfolio.id)
    return g

@portfolio_read_required
def portfolio_projects(request, pk):
  """List of projects within a portfolio"""
  portfolio = Portfolio.objects.get(pk=pk)
  projects = Project.objects.filter(portfolio=portfolio).exclude(is_organization_project=True)
  user_projects = [project for project in projects if request.user.has_perm('view_project', project)]
  anonymous_user = User.objects.get(username='AnonymousUser')
  project_form = ProjectForm(request.user, initial={'portfolio': portfolio.id})
  return render(request, "portfolios/detail.html", {
      "portfolio": portfolio,
      "projects": projects if request.user.has_perm('view_portfolio', portfolio) else user_projects,
      "project_form": project_form,
      "can_invite_to_portfolio": request.user.has_perm('can_grant_portfolio_owner_permission', portfolio),
      "can_edit_portfolio": request.user.has_perm('change_portfolio', portfolio),
      "send_invitation": Invitation.form_context_dict(request.user, portfolio, [request.user, anonymous_user]),
      "users_with_perms": portfolio.users_with_perms(),
      "display_users_with_perms": len(portfolio.users_with_perms()),
      })

# INVITATIONS

@login_required
def send_invitation(request):
    import email_validator
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    try:
        if not request.POST['user_id'] and not request.POST['user_email']:
            raise ValueError("Select a team member or enter an email address.")

        if request.POST['user_email']:
            # Validate that the provided email address is syntactically
            # correct and that the domain name resolved.
            #
            # When we're running tests, skip DNS-based deliverability checks
            # so that tests can be run in a completely offline mode. Otherwise
            # dns.resolver.NoNameservers will result in EmailUndeliverableError.
            email_validator.validate_email(request.POST['user_email'], check_deliverability=settings.VALIDATE_EMAIL_DELIVERABILITY)

        # Get the recipient user
        if len(request.POST.get("user_id")) > 0:
            to_user = get_object_or_404(User, id=request.POST.get("user_id"))
        from_project = None
        from_portfolio = None
        # Find the Portfolio and grant permissions to the user being invited
        if request.POST.get("portfolio"):
          from_portfolio = Portfolio.objects.filter(id=request.POST["portfolio"]).first()
          if len(request.POST.get("user_id")) > 0:
            from_portfolio.assign_edit_permissions(to_user)
            logger.info(
                event="send_invitation portfolio assign_edit_permissions",
                object={"object": "portfolio", "id": from_portfolio.id, "title": from_portfolio.title},
                receiving_user={"id": to_user.id, "username": to_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )

        # Validate that the user is a member of from_project. Is None
        # if user is not a project member.
        elif request.POST.get("project"):
          from_project = Project.objects.filter(id=request.POST["project"]).first()
          if len(request.POST.get("user_id")) > 0:
            from_project.assign_edit_permissions(to_user)
            logger.info(
                event="send_invitation project assign_edit_permissions",
                object={"object": "project", "id": from_project.id, "title":from_project.title},
                receiving_user={"id": to_user.id, "username": to_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            # Assign permissions to view system, root_element
            from_project.system.assign_edit_permissions(to_user)
            logger.info(
                event="send_invitation system assign_edit_permissions",
                object={"object": "system", "id": from_project.system.root_element.id, "name": from_project.system.root_element.name},
                receiving_user={"id": to_user.id, "username": to_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            from_project.system.root_element.assign_edit_permissions(to_user)
            logger.info(
                event="send_invitation element assign_edit_permissions",
                object={"object": "element", "id": from_project.system.root_element.id, "name": from_project.system.root_element.name},
                receiving_user={"id": to_user.id, "username": to_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            messages.add_message(request, messages.INFO, "{} granted edit permission to project.".format(to_user.username))

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
            target = Task.objects.get(id=request.POST["into_task_editorship"])
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
            target = get_object_or_404(Discussion, id=request.POST["into_discussion"])
            if not target.can_invite_guests(request.user):
                return HttpResponseForbidden()
            target_info = {
                "what": "invite-guest",
            }

        elif request.POST.get("portfolio"):
            target = from_portfolio
            target_info = {}
        else:
            target = from_project
            target_info = {
                "what": "join-team",
            }

        inv = Invitation.objects.create(
            from_user=request.user,
            from_project=from_project,
            from_portfolio=from_portfolio,

            # what is the recipient being invited to? validate that the user is an admin of this project
            # or an editor of the task being reassigned.
            into_project=into_project,
            target=target,
            target_info=target_info,

            # who is the recipient of the invitation?
            to_user=User.objects.get(id=request.POST["user_id"]) if len(request.POST.get("user_id")) > 0 else None,
            to_email=request.POST.get("user_email"),

            # personalization
            text=request.POST.get("message", ""),
        )

        inv.send() # TODO: Move this into an asynchronous queue.

        return JsonResponse({ "status": "ok" })

    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })
    except Exception as e:
        logger.error(
            event="send invitation",
            object={"status": "error",
                    "message": " ".join(["There was a problem -- sorry!", str(e)])},
            user={"id": request.user.id, "username": request.user.username}
        )
        return JsonResponse({ "status": "error", "message": "There was a problem -- sorry!" })

@login_required
def cancel_invitation(request):
    inv = get_object_or_404(Invitation, id=request.POST['id'], from_user=request.user)
    inv.revoked_at = timezone.now()
    inv.save(update_fields=['revoked_at'])
    logger.info(
        event="cancel_invitation",
        object={"object": "invitation", "id": inv.id, "to_email": inv.to_email},
        user={"id": request.user.id, "username": request.user.username}
    )
    return JsonResponse({ "status": "ok" })

def accept_invitation(request, code=None):
    assert code.strip() != ""
    inv = get_object_or_404(Invitation, email_invitation_code=code)

    response = accept_invitation_do_accept(request, inv)
    if isinstance(response, HttpResponse):
        return response

    # The invitation has been accepted by a logged in user.
    logger.info(
        event="accept_invitation",
        object={"object": "invitation", "id": inv.id, "to_email": inv.to_email},
        user={"id": request.user.id, "username": request.user.username}
    )

    # Make sure user has a default portfolio
    if len(request.user.portfolio_list()) == 0:
        portfolio = request.user.create_default_portfolio_if_missing()

    # Some invitations create an interstitial before redirecting.
    inv.from_user.preload_profile()
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
    from django.http import HttpResponseRedirect
    import urllib.parse

    # Can't accept if this object has expired. Warn the user but
    # send them to the homepage.
    if inv.is_expired():
        messages.add_message(request, messages.ERROR, 'The invitation you wanted to accept has expired.')
        return HttpResponseRedirect("/")

    # See if the user is ready to accept the invitation.
    if request.user.is_authenticated and request.GET.get("accept-invitation") == "1":
        # When the user first reaches this view they may already be logged
        # into Q but we want to force them to prove their credentials when
        # they accept the invitation. The user may not want to
        # accept the invitation under an account they happened to be logged
        # in as. So accept-invitation is initialy not set and we hit the else condition
        # where we show the invitation acceptance page.
        #
        # We then send them to create an account or log in.
        # The "next" URL on that login screen adds "accept-invitation=1", so that when
        # we come back here, we just accept whatever account they created
        # or logged in to.
        pass

    # elif inv.to_user and request.user == inv.to_user:
    #     # If the invitation was to a user account, and the user is already logged
    #     # in to it, then we're all set.
    #     pass

    # elif inv.to_user:
    #     # If the invitation was to a user account but the user wasn't already logged
    #     # in under that account, then since the user on this request has just demonstrated
    #     # ownership of that user's email address, we can log them in immediately.
    #     matched_user = authenticate(user_object=inv.to_user)
    #     if not matched_user.is_active:
    #         messages.add_message(request, messages.ERROR, 'Your account has been deactivated.')
    #         return HttpResponseRedirect("/")
    #     if request.user.is_authenticated:
    #         # The user was logged into a different account before. Log them out
    #         # of that account and then log them into the account in the invitation.
    #         logout(request) # setting a message after logout but before login should keep the message in the session
    #         messages.add_message(request, messages.INFO, 'You have been logged in as %s.' % matched_user)
    #     login(request, matched_user)

    else:
        # Ask the user to log in or sign up, redirecting back to this page after with
        # "accept-invitation=1" so that we know the user is ready to accept the invitation
        # under the account they are logged in as.
        from urllib.parse import urlencode

        # In the event the user was already logged into an account, and if username/pwd
        # logins are enabled, then log them out now --- we make them log in again or sign
        # up next.
        username_pw_logins_emailed = ('django.contrib.auth.backends.ModelBackend' in settings.AUTHENTICATION_BACKENDS)
        if username_pw_logins_emailed:
            logout(request)

        return render(request, "invitation.html", {
            "inv": inv,
            "next": urlencode({ "next": request.path + "?accept-invitation=1", }),
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
            # Add user to system and root element
            # Grant user permissions to system and root element
            inv.from_project.assign_edit_permissions(request.user)
            logger.info(
                event="accept_invitation project assign_edit_permissions",
                object={"object": "project", "id": inv.from_project.id, "title":inv.from_project.title},
                sending_user={"id": inv.from_user.id, "username": inv.from_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            # Assign permissions to view system, root_element
            inv.from_project.system.assign_edit_permissions(request.user)
            logger.info(
                event="accept_invitation system assign_edit_permissions",
                object={"object": "system", "id": inv.from_project.system.root_element.id, "name":inv.from_project.system.root_element.name},
                sending_user={"id": inv.from_user.id, "username": inv.from_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )
            inv.from_project.system.root_element.assign_edit_permissions(request.user)
            logger.info(
                event="accept_invitation element assign_edit_permissions",
                object={"object": "element", "id": inv.from_project.system.root_element.id, "name":inv.from_project.system.root_element.name},
                sending_user={"id": inv.from_user.id, "username": inv.from_user.username},
                user={"id": request.user.id, "username": request.user.username}
            )

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

@login_required
def organization_settings(request):
    # Authorization. Different users can see different things on
    # this page.
    # This is the settings page for the overall install. There is no specific organization
    # except the entire organization
    can_see_org_settings = True
    # TODO org_admins needs to be selected a different way
    # This approach leverages Django's permission model for admin screens
    org_admins = User.objects.filter(is_staff=True)
    # TODO better selection of who can edit
    # can_edit_org_settings = request.user in org_admins
    can_edit_org_settings = request.user.is_staff
    is_django_staff = request.user.is_staff

    # In 0.9.0 we should only have 1 organization, so let's get that
    # If Instance has been upgraded to 0.9.0 from 0.8.6 there will be multiple organizations,
    #   but we are still going to be looking for the first organization created during install.
    #   This approach is more robust but still brittle. It is possible for an administrator to directly
    #   change the organization database tables resulting in a different organization being "first."
    #   A more robust approach might be adding a field to Organization model to identify the
    #   "main" organization and allow only one main organization to exist.
    # TODO better setting of organization
    organization = Organization.objects.first()

    # If the user doesn't have permission to see anything on this
    # page, give an appropriate HTTP response.
    if not is_django_staff:
        return HttpResponseForbidden("You do not have access to this page.")

    # Get database environment settings
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        db_type = "Postgres"
    elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        db_type = "MySQL"
    elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        db_type = "SQLite"
    else:
        db_type = "Unknown"

    def preload_profiles(users):
        users = list(users)
        User.preload_profiles(users, sort=True)
        return users

    return render(request, "settings.html", {
        "can_edit_org_settings": can_edit_org_settings,
        "is_django_staff": is_django_staff,
        "can_visit_org_in_django_admin": is_django_staff and request.user.has_perm("organization_change"),
        "can_visit_user_in_django_admin": is_django_staff and request.user.has_perm("user_change"),
        "django_admin_url": settings.SITE_ROOT_URL + "/admin",
        "org_admins": preload_profiles(org_admins),
        # TODO better pulling of teams
        "help_squad": preload_profiles(organization.help_squad.all()),
        "reviewers": preload_profiles(organization.reviewers.all()),
        "projects": Project.objects.all(),
        "portfolios": Portfolio.objects.all(),
        "users": User.objects.all(),
        "project_permissions": get_perms_for_model(Project),
        "portfolio_permissions": get_perms_for_model(Portfolio),
        "db_type": db_type,
    })

@login_required
def organization_settings_save(request):
    if request.method != "POST":
        return HttpResponseForbidden()

    # In 0.9.0 we only have 1 organization, so let's get that
    # TODO better setting of organization
    organization = Organization.objects.get(id=1)
    if request.user not in organization.get_organization_project().get_admins():
        return HttpResponseForbidden("You do not have permission.")

    if request.POST.get("action") == "remove-from-org-admins":
        # I don't think organization projects have non-admin members so we
        # remove the entire ProjectMembership. But maybe we should be
        # keeping the ProjectMembership record but just making them a non-admin?
        user = get_object_or_404(User, id=request.POST.get("user"))
        ProjectMembership.objects.filter(
            project=organization.get_organization_project(),
            user=user
        ).delete()
        messages.add_message(request, messages.INFO, '%s has been removed from the list of organization administrator.' % user)
        return JsonResponse({ "status": "ok" })

    if request.POST.get("action") == "remove-from-help-squad":
        user = get_object_or_404(User, id=request.POST.get("user"))
        organization.help_squad.remove(user)
        messages.add_message(request, messages.INFO, '%s has been removed from the help squad.' % user)
        return JsonResponse({ "status": "ok" })

    if request.POST.get("action") == "remove-from-reviewers":
        user = get_object_or_404(User, id=request.POST.get("user"))
        organization.reviewers.remove(user)
        messages.add_message(request, messages.INFO, '%s has been removed from the reviewers.' % user)
        return JsonResponse({ "status": "ok" })

    if request.POST.get("action") == "add-to-org-admins":
        user = get_object_or_404(User, id=request.POST.get("user"))
        mbr, _ = ProjectMembership.objects.get_or_create(
            project=organization.get_organization_project(),
            user=user
        )
        mbr.is_admin = True
        mbr.save()
        messages.add_message(request, messages.INFO, '%s has been made an organization administrator.' % user)
        return JsonResponse({ "status": "ok" })

    if request.POST.get("action") == "add-to-help-squad":
        user = get_object_or_404(User, id=request.POST.get("user"))
        organization.help_squad.add(user)
        messages.add_message(request, messages.INFO, '%s has been added to the help squad.' % user)
        return JsonResponse({ "status": "ok" })

    if request.POST.get("action") == "add-to-reviewers":
        user = get_object_or_404(User, id=request.POST.get("user"))
        organization.reviewers.add(user)
        messages.add_message(request, messages.INFO, '%s has been added to the reviewers.' % user)
        return JsonResponse({ "status": "ok" })

    if request.POST.get("action") == "search-users":
        # TODO: Filter in a database query or else cache the result of get_who_can_read.
        users = list(organization.get_who_can_read())
        users = [user for user in users
            if request.POST.get("query", "").lower().strip() in user.username.lower()
        ]
        users = users[:20] # limit
        return JsonResponse({ "users": [user.render_context_dict() for user in users] })

    return JsonResponse({ "status": "error", "message": str(request.POST) })

def shared_static_pages(request, page):
    from django.utils.module_loading import import_string
    from django.contrib.humanize.templatetags.humanize import intcomma
    password_hasher = import_string(settings.PASSWORD_HASHERS[0])()
    password_hash_method = password_hasher.algorithm.upper().replace("_", " ") \
        + " (" + intcomma(password_hasher.iterations) + " iterations)"

    return render(request,
        page + ".html", {
        "base_template": "base.html",
        "SITE_ROOT_URL": request.build_absolute_uri("/"),
        "password_hash_method": password_hash_method,
        # "project_form": ProjectForm(request.user),
        "project_form": None,
    })

# SUPPORT

def support(request):
    """Render a supoort page with custom content"""

    support_results = Support.objects.all()
    if len(support_results) > 0:
        support = support_results[0]
    else:
        support = {
            "text": "This page has not be set up. Please have admin set up page in Djano admin.",
            "email": None,
            "phone": None,
            "url": None
        }
    return render(request, "support.html", {
        "support": support,
        })

# SINGLE SIGN ON

def sso_logout(request):
    # Log sso_logout
    logger.info(
        event="sso_logout",
        user={"id": request.user.id, "username": request.user.username}
    )
    output = "You are logged out."
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)
