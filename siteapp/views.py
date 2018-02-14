import random

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import User, Folder, Project, Invitation
from guidedmodules.models import Module, ModuleQuestion, Task, ProjectMembership
from discussion.models import Discussion

from .good_settings_helpers import AllauthAccountAdapter # ensure monkey-patch is loaded
from .notifications_helpers import *

def homepage(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/projects")

    from allauth.account.forms import LoginForm
    return render(request, "index.html", {
        "login_form": LoginForm,
    })


def assign_project_lifecycle_stage(projects):
    # Define lifecycle stages.
    # Because we alter this data structure in project_list,
    # we need a new instance of it on every page load.
    lifecycle_stages = [
        {
            "id": "none",
            "label": "General Assessments",
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
    projects = Project.get_projects_with_read_priv(request.user, request.organization)
    projects = [p for p in projects if p.contained_in_folders.all().count() > 0]

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

    return render(request, "projects.html", {
        "lifecycles": lifecycles,
        "is_lonely_admin": request.user.can_see_org_settings and not request.organization.get_who_can_read().exclude(id=request.user.id).exists(),
        "send_invitation": Invitation.form_context_dict(request.user, request.organization.get_organization_project(), [request.user]),
    })


def get_compliance_apps_catalog(organization, reset_cache=False):
    # Load the compliance apps available to the given organization.
    # Since accessing remote AppSources is an expensive operation,
    # cache the catalog information.

    from django.core.cache import cache

    from guidedmodules.models import AppSource

    apps = []

    # For each AppSource....
    for appsrc in AppSource.objects.all():
        # System apps are not listed the compliance apps catalog.
        if appsrc.is_system_source:
            continue

        # If we don't have cached catalog info for this source...
        # (keyed off of the current state of the AppSource instance)
        cache_key = "compliance_catalog_source_{}".format(appsrc.id)
        cache_stale_key = appsrc.make_cache_stale_key()
        cached_apps = cache.get(cache_key, (None, None))
        if cached_apps[0] != cache_stale_key or reset_cache:
            # Connect to the remote app data...
            with appsrc.open() as appsrc_connection:
                # Iterate through all of the apps provided by this source.
                cached_apps = []
                for app in appsrc_connection.list_apps():
                    # Render the catalog info for display.
                    app = render_app_catalog_entry(app)
                    cached_apps.append(app)

                # Cache the results.
                cached_apps = (cache_stale_key, cached_apps)
                cache.set(cache_key, cached_apps)

        # Add the apps in this source to the returned list. But apps
        # from private sources are only listed if the organization
        # is white-listed.
        if not appsrc.available_to_all \
          and organization not in appsrc.available_to_orgs.all():
            continue

        # Add the apps from the cached data structure.
        apps.extend(cached_apps[1])

    return apps

def render_app_catalog_entry(app):
            from guidedmodules.module_logic import render_content

            # Clone, I guess?
            catalog_info = dict(app.get_catalog_info())

            catalog_info["appsource_id"] = app.store.source.id
            catalog_info["key"] = "{source}/{name}".format(source=app.store.source.slug, name=app.name)

            catalog_info.setdefault("description", {})

            catalog_info["description"]["short"] = render_content(
                {
                    "template": catalog_info.get("description", {}).get("short") or "",
                    "format": "markdown",
                },
                None,
                "html",
                "%s %s" % (repr(catalog_info["name"]), "short description")
            )

            catalog_info["description"]["long"] = render_content(
                {
                    "template": catalog_info.get("description", {}).get("long")
                        or catalog_info.get("description", {}).get("short")
                        or "",
                    "format": "markdown",
                },
                None,
                "html",
                "%s %s" % (repr(catalog_info["name"]), "short description")
            )

            catalog_info["search_haystak"] = "".join([
                app.name,
                catalog_info["title"],
                catalog_info.get("vendor", ""),
                catalog_info["description"]["short"],
                catalog_info["description"]["long"],
            ])

            # Convert the app icon raw bytes data to a data URL.
            if "app-icon" in catalog_info:
                from guidedmodules.models import image_to_dataurl
                catalog_info["app_icon_dataurl"] = image_to_dataurl(catalog_info["app-icon"], 128)

            return catalog_info


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
            raise ValueError("Question does not expect a protocol.")
        filter_protocols = set(question.spec["protocol"])
    elif isinstance(filter_protocols, (list, set)):
        # A list or set of protocol IDs is passed. Turn it into a set if it isn't already.
        filter_protocols = set(filter_protocols)
    else:
        raise ValueError(filter_protocols)

    # Get the protocols implemented by the app.
    if isinstance(app.get("protocol"), str):
        # Just one - wrap in a set().
        app_protocols = { app["protocol"] }
    elif isinstance(app.get("protocol"), list):
        # It's an array. Unique-ify with a set.
        app_protocols = set(app["protocol"])
    else:
        # no protocol or invalid data type
        app_protocols = set()

    # Check that every protocol required by the question is implemented by the
    # app.
    return filter_protocols <= set(app_protocols)


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
        filter_description = None

    return catalog, filter_description


@login_required
def apps_catalog(request):
    # A POST from a Django user with permission on AppSources
    # clears the catalog cache.
    can_clear_catalog_cache = request.user.has_perm('guidedmodules.appsource_change')
    if request.method == "POST" and can_clear_catalog_cache:
        get_compliance_apps_catalog(request.organization, reset_cache=True)
        return HttpResponseRedirect(request.path)

    # We use the querystring to remember which question the user is selecting
    # an app to answer, when starting an app from within a project.
    from urllib.parse import urlencode
    forward_qsargs = { }
    if "q" in request.GET: forward_qsargs["q"] = request.GET["q"]

    # Get the app catalog. If the user is answering a question, then filter to
    # just the apps that can answer that question.
    from guidedmodules.module_sources import AppSourceConnectionError
    try:
        catalog, filter_description = filter_app_catalog(get_compliance_apps_catalog(request.organization), request)
    except (ValueError, AppSourceConnectionError) as e:
        return render(request, "app-store.html", {
            "error": e,
            "apps": [],
        })        

    # Group by category from catalog metadata.
    from collections import defaultdict
    catalog_by_category = defaultdict(lambda : { "title": None, "apps": [] })
    for app in catalog:
        for category in app.get("categories", [app.get("category")]):
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

    return render(request, "app-store.html", {
        "apps": catalog_by_category,
        "filter_description": filter_description,
        "forward_qsargs": ("?" + urlencode(forward_qsargs)) if forward_qsargs else "",
        "can_clear_catalog_cache": can_clear_catalog_cache,
    })

@login_required
def apps_catalog_item(request, app_namespace, app_name):
    # Is this a module the user has access to? The app store
    # does some authz based on the organization.
    from guidedmodules.models import AppSource
    for app_catalog_info in get_compliance_apps_catalog(request.organization):
        if app_catalog_info["key"] == app_namespace + "/" + app_name:
            # We found it.
            break
    else:
        raise Http404()

    if request.method == "GET":
        # Show the "app" page.

        return render(request, "app-store-item.html", {
            "first": not ProjectMembership.objects.filter(user=request.user, project__organization=request.organization).exists(),
            "app": app_catalog_info,
        })
    
    else:
        # Start the app.

        if not request.GET.get("q"):
            # Since we no longer ask what folder to put the new Project into,
            # create a default Folder instance for all started apps that aren't
            # answers to questions. All top-level apps must be in a folder. That's
            # how we know to display it in the project_list view.
            default_folder_name = "Started Apps"
            folder = Folder.objects.filter(
                organization=request.organization,
                admin_users=request.user,
                title=default_folder_name,
            ).first()
            if not folder:
                folder = Folder.objects.create(organization=request.organization, title=default_folder_name)
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

        project = start_app(app_catalog_info, request.organization, request.user, folder, task, q)

        if task and q:
            # Redirect to the task containing the question that was just answered.
            from urllib.parse import urlencode
            return HttpResponseRedirect(task.get_absolute_url() + "#" + urlencode({ "q": q.key }))

        # Redirect to the new project.
        return HttpResponseRedirect(project.get_absolute_url())


def start_app(app_catalog_info, organization, user, folder, task, q):
    from guidedmodules.models import AppSource

    # If the first argument is a string, it's an app id of the
    # form "source/appname". Get the catalog info.
    if isinstance(app_catalog_info, str):
        for app in get_compliance_apps_catalog(organization):
            if app["key"] == app_catalog_info:
                # We found it.
                app_catalog_info = app
                break
        else:
            raise ValueError("{} is not an app in the catalog.".format(app_catalog_info))

    # Begin a transaction to create the Module and Task instances for the app.
    with transaction.atomic():
        module_source = get_object_or_404(AppSource, id=app_catalog_info["appsource_id"])

        # Turn the app catalog entry into an App instance,
        # and then import it into the database as Module instance.
        if app_catalog_info["authz"] == "none":
            # We can instantiate the app immediately.
            # 1) Get the connection to the AppSource.
            with module_source.open() as store:
                # 2) Get the App.
                app_name = app_catalog_info["key"][len(module_source.slug)+1:]
                app = store.get_app(app_name)

                # 3) Re-validate that the catalog information is the same.
                if app.get_catalog_info()["authz"] != "none":
                    raise ValueError("Invalid access.")

                # 4) Import. Use the module named "app".
                appinst = app.import_into_database()
                module = appinst.modules.get(module_name="app")

        else:
            # Create a stub Module -- we'll download the app later. This
            # is just a placeholder.
            module = Module()
            module.source = module_source
            # TODO module.app = None
            module.module_name = "app"
            module.spec = dict(app_catalog_info)
            module.spec["type"] = "project"
            module.spec["is_app_stub"] = True
            module.save()

        # Create project.
        project = Project()
        project.organization = organization

        # Save and add to folder
        project.save()
        project.set_root_task(module, user)
        if folder:
            folder.projects.add(project)

        # Add user as the first admin.
        ProjectMembership.objects.create(
            project=project,
            user=user,
            is_admin=True)

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
        project = get_object_or_404(Project, id=project_id, organization=request.organization)

        # Check authorization.
        if not project.has_read_priv(request.user):
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

    can_start_task = project.can_start_task(request.user)

    # Collect all of the questions and answers, i.e. the sub-tasks, that we'll display.
    questions = { }
    first_start = True
    can_start_any_apps = False
    for (mq, is_answered, answer_obj, answer_value) in root_task_answers.answertuples.values():
        # Display module/module-set questions only. Other question types in a project
        # module are not valid.
        if mq.spec.get("type") not in ("module", "module-set"):
            continue

        # Skip questions that are imputed.
        if is_answered and not answer_obj:
            continue

        # Is this question answered yet? Are there any discussions the user
        # is a guest of in any of the tasks that answer this question?
        is_finished = None
        progress_percent = 0
        tasks = []
        task_discussions = []
        if answer_value is not None:
            if mq.spec["type"] == "module":
                # Convert a ModuleAnswers instance to an array containing just itself.
                answer_value = [answer_value]
            elif mq.spec["type"] == "module-set":
                # ans is already a list of ModuleAnswers instances.
                pass
            for module_answers in answer_value:
                task = module_answers.task

                task_discussions.extend([d for d in discussions if d.attached_to.task == task])
                
                tasks.append(task)
                if not task.is_finished():
                    # If any task is unfinished, the whole question
                    # is marked as unfinished.
                    is_finished = False
                elif is_finished is None:
                    # If all tasks are finished, the whole question
                    # is marked as finished.
                    is_finished = True

                if len(answer_value) == 1:
                    progress_percent = task.get_progress_percent()

        # Do not display if the user can't start a task and there are no
        # tasks visible to the user.
        if not can_start_task and len(tasks) == 0 and len(task_discussions) == 0:
            continue

        # Is this the first Start?
        d_first_start = first_start and (len(tasks) == 0)
        if d_first_start: first_start = False

        # Is this a protocol question?
        if mq.spec.get("protocol"):
            # Set flag if an app can be started here.
            if can_start_task and (answer_value is None or mq.spec["type"] == "module-set"):
                can_start_any_apps = True

        # Create template context dict for this question.
        questions[mq.id] = {
            "question": mq,
            "is_finished": is_finished,
            "progress_percent": progress_percent,
            "tasks": tasks,
            "can_start_new_task": mq.spec["type"] == "module-set" or len(tasks) == 0,
            "first_start": d_first_start,
            "discussions": task_discussions,
            "invitations": [], # filled in below
        }

        # If the question specification specifies an icon asset, load the asset.
        # This saves the browser a request to fetch it, which is somewhat
        # expensive because assets are behind authorization logic.
        if "icon" in mq.spec:
            questions[mq.id]["icon"] = project.root_task.get_static_asset_image_data_url(mq.spec["icon"], 75)


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
            { "title": "Backlog" },
            { "title": "Selected" },
            { "title": "Implement / Update" },
            { "title": "Assessment" },
        ]
        for column in columns:
            column["questions"] = []

        for question in main_area_questions:
            #import random
            #random.choice(columns[0:1+random.choice(range(len(columns)))])["questions"].append(question)

            if len(question["tasks"]) == 0:
                col = 0
                question["hide_icon"] = True
            elif question["question"].spec["type"] == "module-set":
                if question["is_finished"]:
                    col = 3
                else:
                    col = 2
            elif question["tasks"][0].is_finished():
                col = 3
            elif question["tasks"][0].is_started():
                col = 2
            else:
                col = 1
            columns[col]["questions"].append(question)


    # Assign questions in columns to groups.
    from collections import OrderedDict
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

        column["has_tasks_on_left"] = ((i > 0) and (columns[i-1]["groups"] or columns[i-1]["has_tasks_on_left"]))

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
        "page_title": "Components",
        "project": project,

        "is_admin": request.user in project.get_admins(),
        "can_start_task": can_start_task,
        "can_start_any_apps": can_start_any_apps,

        "title": project.title,
        "open_invitations": other_open_invitations,
        "send_invitation": Invitation.form_context_dict(request.user, project, [request.user]),
        "has_outputs": has_outputs,

        "layout_mode": layout_mode,
        "columns": columns,
        "action_buttons": action_buttons,

        "authoring_tool_enabled": project.root_task.module.is_authoring_tool_enabled(request.user),
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
            templates.append(header[format](anchor, title) + doc["template"])
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
                for key, value in node.items():
                    if "." in key: continue # a read-only field
                    flatten_json(path+[key], value, output)
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

        from django.contrib import messages
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
        organization=request.organization,
        title=request.POST.get("title") or "New Folder",
    )
    f.admin_users.add(request.user)
    return JsonResponse({ "status": "ok", "id": f.id, "title": f.title })


def project_admin_login_post_required(f):
    # Wrap the function to do authorization and change arguments.
    def g(request, project_id, *args):
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
def rename_project(request, project):
    # Update the project's title, which is actually updating its root_task's title_override.
    # If the title isn't changing, don't store it. If the title is set to empty, clear the
    # override.
    title = request.POST.get("title", "").strip() or None
    project.root_task.title_override = title
    project.root_task.save()
    project.root_task.on_answer_changed()
    return JsonResponse({ "status": "ok" })

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
def export_project(request, project):
    from urllib.parse import quote
    data = project.export_json(include_metadata=True, include_file_content=True)
    resp = JsonResponse(data, json_dumps_params={"indent": 2})
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
        project.import_json(data, request.user, "imp", lambda x : log_output.append(x))
    except Exception as e:
        log_output.append(str(e))

    # Show an unfriendly response containing log output.
    return JsonResponse(log_output, safe=False, json_dumps_params={"indent": 2})


def project_start_apps(request, *args):
    # Load the Compliance Store catalog of apps.
    all_apps = get_compliance_apps_catalog(request.organization)

    # What questions can be answered with an app?
    def get_questions(project):
        # A question can be answered with an app if it is a module or module-set
        # question with a protocol value and the question has not already been
        # answered (inclding imputed).
        root_task_answers = project.root_task.get_answers().with_extended_info().as_dict()
        for q in project.root_task.module.questions.order_by('definition_order'):
            if    q.spec["type"] in ("module", "module-set") \
             and  q.spec.get("protocol") \
             and q.key not in root_task_answers:
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
            # chosen app satisfies the protocol.
            errored_questions = []
            for q in get_questions(project):
                if q.key in request.POST:
                    startable_apps = { app["key"]: app for app in q.startable_apps}
                    if request.POST[q.key] in startable_apps:
                        app = startable_apps[request.POST[q.key]]
                        try:
                            start_app(app, request.organization, request.user, None, project.root_task, q)
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
                        appname=app["name"],
                        title=q.spec["title"],
                        key=q.key,
                        error=error,
                    )
                    for q, app, error in errored_questions
                )
                return JsonResponse({ "status": "error", "message": message })

    return viewfunc(request, *args)

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
    
    if request.user.is_authenticated and request.GET.get("accept-auth") == "1":
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
        if request.user.is_authenticated:
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

