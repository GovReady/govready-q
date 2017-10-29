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
    if request.user.is_authenticated:
        return HttpResponseRedirect("/projects")

    from allauth.account.forms import LoginForm
    return render(request, "index.html", {
        "login_form": LoginForm,
    })

def folder_list(request):
    # Get the folders the user can see. Folders are accessible to a user
    # just when they can see a Project within it or if they
    # are an admin of the folder, so we go backwards from Projects
    projects = Project.get_projects_with_read_priv(request.user, request.organization)
    folders = (Folder.objects.filter(projects__in=projects)
            | Folder.objects.filter(organization=request.organization, admin_users=request.user))\
          .distinct()

    # Count up the total number of projects in each folder. For admins, so they
    # can know why they can't delete a folder.
    from django.db.models import Count
    folders = folders.annotate(project_count=Count('projects'))

    # Mark whether the user is an admin of any folders.
    folders = list(folders)
    for folder in folders:
        folder.is_admin = (request.user in folder.get_admins())

    # Sort the folders by name.
    folders.sort(key = lambda folder : folder.title)

    # don't show the prompt to complete account settings in the banner,
    # we'll show it ourselves
    request.suppress_prompt_banner = True

    return render(request, "folder_list.html", {
        "folders": folders,
        "is_lonely_admin": request.user.can_see_org_settings and not request.organization.get_who_can_read().exclude(id=request.user.id).exists(),
        "send_invitation": Invitation.form_context_dict(request.user, request.organization.get_organization_project(), [request.user]),
    })


def folder_view(request, folder_id):
    # Get the folder.
    folder = get_object_or_404(Folder, id=folder_id, organization=request.organization)
    is_admin = (request.user in folder.get_admins())

    # Get the projects that are in the folder that the user can see. This also handily
    # sets user_is_admin on the projects.
    projects = folder.get_readable_projects(request.user)

    # Count up the open tasks in each project.
    for p in projects:
        p.open_tasks = p.get_open_tasks(request.user) # for the template

    # Check authorization. Users can see folders just when they are an admin or they
    # can see any project within it.
    if not is_admin and len(projects) == 0:
        return HttpResponseForbidden()

    # Redirect if slug is not canonical. We do this after checking for
    # read privs so that we don't reveal the folder's title to unpriv'd users.
    if request.path != folder.get_absolute_url():
        return HttpResponseRedirect(folder.get_absolute_url())

    # Count the number of projects in the folder the user can't see in case,
    # as a folder admin, there are projects the user can't see that block
    # deleting the folder.
    total_projcts = folder.projects.count()
    num_hidden_projects = folder.projects.count() - len(projects)

    return render(request, "folder_view.html", {
        "folder": folder,
        "is_admin": is_admin,
        "projects": projects,
        "num_hidden_projects": num_hidden_projects,
        "any_have_members_besides_me": ProjectMembership.objects.filter(project__in=projects).exclude(user=request.user),
    })


# Cache the contents of the app store by the organization, since we
# may show different apps on different organization sites.
_app_store_cache = { }
def get_app_store(request):
    global _app_store_cache
    if request.organization not in _app_store_cache:
        _app_store_cache[request.organization] = list(load_app_store(request.organization))
    return _app_store_cache[request.organization]

def load_app_store(organization):
    from guidedmodules.models import AppSource
    from guidedmodules.module_sources import MultiplexedAppStore
    from guidedmodules.module_logic import render_content

    with MultiplexedAppStore(ms for ms in AppSource.objects.all()) as store:
        for app in store.list_apps():
            # System apps are not listed the app store.
            if app.store.source.namespace == "system":
                continue

            # Apps from private sources are only listed if the organization
            # is white-listed.
            if not app.store.source.available_to_all \
              and organization not in app.store.source.available_to_orgs.all():
                continue

            catalog_info = dict(app.get_catalog_info())

            catalog_info["appsource_id"] = app.store.source.id
            catalog_info["key"] = "{source}/{name}".format(source=app.store.source.namespace, name=app.name)

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

            # Convert the app icon to a data URL.
            if "app-icon" in catalog_info:
                import io, base64
                from PIL import Image
                im = Image.open(io.BytesIO(catalog_info["app-icon"]))
                im.thumbnail((128,128))
                buf = io.BytesIO()
                im.save(buf, 'png')
                catalog_info["app_icon_dataurl"] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

            yield catalog_info

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


def app_satifies_interface(app, question):
    # Does this question specify a protocol? It must specify a list of protocols.
    if not isinstance(question.spec.get("protocol"), list):
        raise ValueError("Question does not expect a protocol.")

    # Get the protocols implemented by the app.
    if isinstance(app.get("protocol"), str):
        # Wrap a single protocol string in an array.
        protocols = [app["protocol"]]
    elif isinstance(app.get("protocol"), list):
        # It's an array.
        protocols = app["protocol"]
    else:
        # no protocol or invalid data type
        protocols = set()

    # Check that every protocol required by the question is implemented by the
    # app.
    return set(question.spec["protocol"]) <= set(protocols)


def filter_app_catalog(catalog, request):
    filter_description = None

    if request.GET.get("q"):
        # Check if the app satisfies the interface.
        task, q = get_task_question(request)
        catalog = filter(lambda app : app_satifies_interface(app, q), catalog)
        filter_description = q.spec["title"]

    return catalog, filter_description


@login_required
def app_store(request):
    # We use the querystring to remember which question the user is selecting
    # an app to answer, when starting an app from within a project.
    from urllib.parse import urlencode
    forward_qsargs = { }
    if "q" in request.GET: forward_qsargs["q"] = request.GET["q"]

    # Get the app catalog. If the user is answering a question, then filter to
    # just the apps that can answer that question.
    from guidedmodules.module_sources import AppSourceConnectionError
    try:
        catalog, filter_description = filter_app_catalog(get_app_store(request), request)
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
    })

@login_required
def app_store_item(request, app_namespace, app_name):
    # Is this a module the user has access to? The app store
    # does some authz based on the organization.
    from guidedmodules.models import AppSource
    for app_catalog_info in get_app_store(request):
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
        # Show the form to start the app.

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

            if len(folders) > 0 and ("q" not in request.GET):
                add_to_folder = ChoiceField(
                    choices=[(f.id, f) for f in folders] + [("", "Create a new folder")],
                    required=False,
                    label="Add this app to which project folder?",
                    widget=RadioSelect)

        if "firstsubmit" in request.POST and "q" not in request.GET:
            # When coming to this page for the first time, don't do validation since
            # nothing has been submitted yet. Unless the 'q' are is specified, in
            # which case there are no form items and we can submit immediately.
            form = NewProjectForm()
        else:
            form = NewProjectForm(request.POST)
            if not form.errors:
                if not request.GET.get("q"):
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
                            title=app_catalog_info["title"] + " started on " + timezone.now().strftime("%x %X"))

                    # This app is going into a folder. It does not answer a task question.
                    task, q = (None, None)
                else:
                    # This app is going to answer a question.
                    # Don't put it into a folder.
                    folder = None #  task.project.contained_in_folders.first()

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

        # Show form.
        return render(request, "app-store-item-start.html", {
            "app": app_catalog_info,
            "form": form,
        })


def start_app(app_catalog_info, organization, user, folder, task, q):
    from guidedmodules.models import AppSource
    from guidedmodules.module_sources import AppStore

    with transaction.atomic():
        module_source = get_object_or_404(AppSource, id=app_catalog_info["appsource_id"])

        # Turn the app catalog entry into an App instance,
        # and then import it into the database as Module instance.
        if app_catalog_info["authz"] == "none":
            # We can instantiate the app immediately.
            # 1) Get the AppStore instance from the AppSource.
            with AppStore.create(module_source) as store:
                # 2) Get the App.
                app_name = app_catalog_info["key"][len(module_source.namespace)+1:]
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

        # Assign a good title.
        project.title = app_catalog_info["title"]
        if folder:
            projects_in_folder = folder.get_readable_projects(user)
            existing_project_titles = [p.title for p in projects_in_folder]
            ctr = 0
            while project.title in existing_project_titles:
                ctr += 1
                project.title = app_catalog_info["title"] + " " + str(ctr)

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
    # Get all of the discussions I'm participating in as a guest in this project.
    # Meaning, I'm not a member, but I still need access to certain tasks and
    # certain questions within those tasks.
    discussions = list(project.get_discussions_in_project_as_guest(request.user))

    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    root_task_answers = project.root_task.get_answers().with_extended_info()

    can_begin_module = project.can_start_task(request.user)

    # Create all of the module entries in a tabs & groups data structure.
    from collections import OrderedDict
    tabs = OrderedDict()
    action_buttons = []
    question_dict = { }
    first_start = True
    can_start_any_apps = False
    layout_mode = "rows"
    for mq in project.root_task.module.questions.all()\
        .select_related("answer_type_module")\
        .order_by('definition_order'):
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
                
                tasks.append(task)
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

        # Is this a protocol question?
        if mq.spec.get("protocol"):
            # Switch to grid layout.
            layout_mode = "grid"

            # Set flag if an app can be started here.
            if can_begin_module and (ans is None or mq.spec["type"] == "module-set"):
                can_start_any_apps = True

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

        # What icon to show? (If there's an app, it'll use the app's icon instead.)
        # Pre-load the icon as a data URL so that the browser doesn't have to make
        # another request, and since assets are behind auth this'll avoid db logic.
        if "icon" in mq.spec:
            d["icon"] = project.root_task.get_static_asset_image_data_url(mq.spec["icon"], 75)

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
                if into_new_task_question_id in question_dict: # should always be True
                    question_dict[into_new_task_question_id]["invitations"].append(inv)
                    continue

        # If the invitation didn't get put elsewhere, display in the
        # other list.                
        other_open_invitations.append(inv)

    # Render.
    folder = project.primary_folder()
    return render(request, "project.html", {
        "is_project_page": True,
        "project": project,

        "is_admin": request.user in project.get_admins(),
        "can_begin_module": can_begin_module,
        "can_start_any_apps": can_start_any_apps,

        "folder": folder,
        "is_folder_admin": folder and (request.user in folder.get_admins()),

        "title": project.title,
        "intro" : project.root_task.render_field('introduction') if project.root_task.module.spec.get("introduction") else "",
        "open_invitations": other_open_invitations,
        "send_invitation": Invitation.form_context_dict(request.user, project, [request.user]),
        "tabs": list(tabs.values()),
        "action_buttons": action_buttons,
        "has_outputs": has_outputs,

        "layout_mode": layout_mode,
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
            "answers": [],
        }
        sections.append(section)

        # Append all of the questions and answers.
        for q, a, value_display in answers.render_answers(show_unanswered=False, show_imputed=False):
            section["answers"].append((q, a, value_display))

        if len(path) == 0:
            path = path + [task.render_title()]

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
        "project": project,
        "folder": project.primary_folder(),
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
    }
    joiner = {
        "markdown": "\n\n",
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
        "project": project,
        "folder": project.primary_folder(),
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
        "project": project,
        "folder": project.primary_folder(),
        "SITE_ROOT_URL": settings.SITE_ROOT_URL,
        "sample": format_sample(sample),
        "sample_post_keyvalue": sample_post_keyvalue,
        "sample_post_json": format_sample(sample_post_json),
        "schema": schema,
    })

@login_required
def show_api_keys(request):
    # Initialize on first use.
    if request.user.api_key_ro is None:
        request.user.reset_api_keys()

    # Reset.
    if request.method == "POST" and request.POST.get("method") == "resetkeys":
        request.user.reset_api_keys()

        from django.contrib import messages
        messages.add_message(request, messages.INFO, 'Your API keys have been reset.')

        return HttpResponseRedirect(request.path)

    return render(request, "api-keys.html", {
        "api_key_ro": request.user.api_key_ro,
        "api_key_rw": request.user.api_key_rw,
        "api_key_wo": request.user.api_key_wo,
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
def set_folder_description(request):
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])

    # Get the folder.
    folder = get_object_or_404(Folder, id=request.POST.get("folder"))

    # Validate that the user can edit it.
    if request.user not in folder.get_admins():
        return JsonResponse({ "status": "error", "message": "Not authorized." })

    # Update.
    folder.description = request.POST.get("value")
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
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({ "status": "error", "message": "The title cannot be empty." })
    project.title = title
    project.save()
    return JsonResponse({ "status": "ok" })

@project_admin_login_post_required
def delete_project(request, project):
    if not project.is_deletable():
        return JsonResponse({ "status": "error", "message": "This project cannot be deleted." })
    
    parent = project.get_parent_object()
    project.delete()

    # After deleting a project, a folder can become unreadable.
    if isinstance(parent, Folder) and not parent.has_read_priv(request.user):
        parent = None

    redirect = parent.get_absolute_url() if parent else "/"

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
    all_apps = get_app_store(request)

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
                "folder": project.primary_folder(),
                "questions": list(get_questions(project)),
            })
    else:
        @project_admin_login_post_required
        def viewfunc(request, project):
            # Start all of the indiciated apps. Validate that the
            # chosen app satisfies the protocol.
            for q in get_questions(project):
                if q.key in request.POST:
                    startable_apps = { app["key"]: app for app in q.startable_apps}
                    if request.POST[q.key] in startable_apps:
                        app = startable_apps[request.POST[q.key]]
                        start_app(app, request.organization, request.user, None, project.root_task, q)

            return JsonResponse({ "status": "ok" }, safe=False, json_dumps_params={"indent": 2})

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

