from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

import re

from .models import Module, ModuleQuestion, Task, TaskAnswer, TaskAnswerHistory, InstrumentationEvent

import guidedmodules.module_logic as module_logic
import guidedmodules.answer_validation as answer_validation
from discussion.models import Discussion
from siteapp.models import User, Invitation, Project, ProjectMembership
from siteapp.forms import ProjectForm

import fs, fs.errors

@login_required
def new_task(request):
    # Create a new task by answering a module question of a project rook task.
    project = get_object_or_404(Project, id=request.POST["project"])

    # Can the user create a task within this project?
    if not project.can_start_task(request.user):
        return HttpResponseForbidden()

    # Create the new subtask.
    task = project.root_task.get_or_create_subtask(request.user, request.POST["question"])

    # Redirect.
    url = task.get_absolute_url()
    if request.POST.get("previous"):
        import urllib.parse
        url += "?" + urllib.parse.urlencode({ "previous": request.POST.get("previous") })
    return HttpResponseRedirect(url)

@login_required
def download_module_asset(request, taskid, taskslug, asset_path):
    # Get the Task and check that the user has read permission.
    task = get_object_or_404(Task, id=taskid)
    if not task.has_read_priv(request.user): raise Http404()

    # Check that this path is one of app's assets.
    if asset_path not in task.module.app.asset_paths:
        raise Http404()

    # Look up the ModuleAsset object.
    content_hash = task.module.app.asset_paths[asset_path]
    asset = task.module.app.asset_files.get(content_hash=content_hash)

    # Get the dbstorage.models.StoredFile instance which holds
    # an auto-detected mime type.
    from dbstorage.models import StoredFile
    sf = StoredFile.objects.only("mime_type").get(path=asset.file.name)

    # Construct the response. The file content is probably untrusted, in which
    # case it must not be served as an inline resource from our domain unless it is
    # an image, which browsers won't execute.
    if (sf.mime_type and sf.mime_type.startswith("image/")) or task.module.app.trust_assets:
        mime_type = sf.mime_type
        disposition = "inline"
    else:
        mime_type = "application/octet-stream"
        disposition = "attachment"

    import os.path
    resp = HttpResponse(asset.file, content_type=mime_type)
    resp['Content-Disposition'] = disposition + '; filename=' + os.path.basename(asset.file.name)

    # Browsers may guess the MIME type if it thinks it is wrong. Prevent
    # that so that if we are forcing application/octet-stream, it
    # doesn't guess around it and make the content executable.
    resp['X-Content-Type-Options'] = 'nosniff'

    # Browsers may still allow HTML to be rendered in the browser. IE8
    # apparently rendered HTML in the context of the domain even when a
    # user clicks "Open" in an attachment-disposition response. This
    # prevents that. Doesn't seem to affect anything else (like images).
    resp['X-Download-Options'] = 'noopen'

    return resp

# decorator for pages that render tasks
def task_view(view_func):
    @login_required
    def new_view_func(request, taskid, taskslug, pagepath, question_key, *args):
        # Get the Task.
        task = get_object_or_404(Task, id=taskid)

        # If this task is actually a project root, redirect away from here.
        # Only do this for GET requests since POST requests can be API-like things.
        if request.method == "GET" and task.root_of.first() is not None:
            return HttpResponseRedirect(task.root_of.first().get_absolute_url())

        # Is this page about a particular question?
        question = None
        if pagepath == "/question/":
            question = get_object_or_404(ModuleQuestion, module=task.module, key=question_key)
            taskans = TaskAnswer.objects.filter(task=task, question=question).first()

        # Does the user have read privs here?
        def read_priv():
            # Yes if they have read privs on the task in general...
            if task.has_read_priv(request.user, allow_access_to_deleted=True):
                # See below for checking if the task was deleted.
                return True

            # Yes if they are a guest in a discussion on this page. This applies
            # to the show-question page only, where we know which question is
            # being asked from the URL.
            if taskans:
                d = Discussion.get_for(task.project.organization, taskans)
                if d and d.is_participant(request.user):
                    return True

            # Yes in the special case of user accessing the avatar of another user
            # TODO: Re-evaluate this code block after implementing a more traditional
            #       user profile model instead of using a Q module for a persons profile.
            #       see https://github.com/GovReady/govready-q/issues/632
            if question_key == "picture":
                return True

            return False
        if not read_priv():
            return HttpResponseForbidden("You do not have read privileges to this page.")

        # We skipped the check for whether the Task is deleted above. Now
        # check for that and provide a more specific error.
        if task.deleted_at:
            # The Task is deleted. If the user would have had access to it,
            # show a more friendly page than an access denied. Discussion
            # guests will have been denied above because is_participant
            # will fail on deleted tasks.
            return HttpResponse("This module was deleted by a project administrator.")

        # Redirect if slug is not canonical. We do this after checking for
        # read privs so that we don't reveal the task's slug to unpriv'd users.
        # Only issue a redirect on GET requests. Since a POST might be saving
        # data, it's fine if the path isn't canonical and we want to allow the
        # save to complete. Also skip if the extra positional args 'args' has
        # any values, which means we're on some subpage that we don't know
        # how to re-form the URL for at the moment.
        if request.method == "GET" and taskslug != task.get_slug() and len(args) == 0:
            return HttpResponseRedirect(task.get_absolute_url() + pagepath + question_key)

        # Load the answers the user has saved so far, and fetch imputed
        # answers and next-question info.
        answered = task.get_answers().with_extended_info()

        # Common context variables.
        context = {
            "DEBUG": settings.DEBUG,
            "ADMIN_ROOT_URL": settings.SITE_ROOT_URL + "/admin",

            "m": task.module,
            "task": task,
            "is_discussion_guest": not task.has_read_priv(request.user), # i.e. only here for discussion
            "write_priv": task.has_write_priv(request.user),
            "is_admin": request.user in task.project.get_admins(),
            "send_invitation": Invitation.form_context_dict(request.user, task.project, [task.editor]),
            "open_invitations": task.get_open_invitations(request.user),
            "source_invitation": task.get_source_invitation(request.user),
            "previous_page_type": request.GET.get("previous"),
        }

        # Render the view.
        return view_func(request, task, answered, context, question, *args)
    return new_view_func

@task_view
def next_question(request, task, answered, *unused_args):
    import urllib.parse
    previous = ("?" + urllib.parse.urlencode({ "previous": request.GET["previous"]})) \
        if "previous" in request.GET else ""

    if len(answered.can_answer) == 0:
        # There is no next question. Redirect to the module finished page.
        return HttpResponseRedirect(task.get_absolute_url() + "/finished" + previous)

    else:
        # Display next unanswered question.
        q = answered.can_answer[0]
        return HttpResponseRedirect(task.get_absolute_url_to_question(q) + previous)

@task_view
def save_answer(request, task, answered, context, __):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # does user have write privs?
    if not task.has_write_priv(request.user):
        return HttpResponseForbidden()

    # normal redirect - load next linear question if possible
    if request.POST.get("next_linear_question"):
        redirect_to = request.POST["next_linear_question"] + "?previous=nquestion"
    else:
        redirect_to = task.get_absolute_url() + "?previous=nquestion"

    # validate question
    q = task.module.questions.get(id=request.POST.get("question"))

    # validate and parse value
    if request.POST.get("method") == "clear":
        # Clear means that the question returns to an unanswered state.
        # This method is only offered during debugging to make it easier
        # to test the application's behavior when questions are unanswered.
        value = None
        cleared = True
        skipped_reason = None
        unsure = False
    
    elif request.POST.get("method") == "skip":
        # The question is being skipped, i.e. answered with a null value,
        # because the user doesn't know the answer, it doesn't apply to
        # the user's circumstances, or they want to return to it later.
        value = None
        cleared = False
        skipped_reason = request.POST.get("skipped_reason") or None
        unsure = bool(request.POST.get("unsure"))

    elif request.POST.get("method") == "save":
        # load the answer from the HTTP request
        if q.spec["type"] == "file":
            # File uploads come through request.FILES.
            value = request.FILES.get("value")

            # We allow the user to preserve the existing uploaded value
            # for a question by submitting nothing. (The proper way to
            # clear it is to use Skip.) If the user submits nothing,
            # just return immediately.
            if value is None:
                return JsonResponse({ "status": "ok", "redirect": redirect_to })

        else:
            # All other values come in as string fields. Because
            # multiple-choice comes as a multi-value field, we get
            # the value as a list. question_input_parser will handle
            # turning it into a single string for other question types.
            value = request.POST.getlist("value")

        # parse & validate
        try:
            value = answer_validation.question_input_parser.parse(q, value)
            value = answer_validation.validator.validate(q, value)
        except ValueError as e:
            # client side validation should have picked this up
            return JsonResponse({ "status": "error", "message": str(e) })

        cleared = False
        skipped_reason = None
        unsure = bool(request.POST.get("unsure"))

    elif request.POST.get("method") == "review":
        # Update the reviewed flag on the answer.
        if not task.has_review_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You are not an organization reviewer." })
        ta = TaskAnswer.objects.filter(task=task, question=q).first()
        if ta:
            ans = ta.get_current_answer()
            if ans and not ans.cleared and ans.id == int(request.POST["answer"]):
                ans.reviewed = int(request.POST["reviewed"])
                ans.save(update_fields=["reviewed"])
                return JsonResponse({ "status": "ok" })
        return JsonResponse({ "status": "error", "message": "Invalid question." })

    else:
        raise ValueError("invalid 'method' parameter %s" + request.POST.get("method", "<not set>"))

    # save answer - get the TaskAnswer instance first
    question, _ = TaskAnswer.objects.get_or_create(
        task=task,
        question=q,
    )

    # fetch the task that answers this question
    answered_by_tasks = []
    if q.spec["type"] in ("module", "module-set") and not cleared:
        if value == "__new":
            # Create a new task, and we'll redirect to it immediately.
            t = Task.create(
                parent_task_answer=question, # for instrumentation only, doesn't go into Task instance
                editor=request.user,
                project=task.project,
                module=q.answer_type_module)

            answered_by_tasks = [t]
            redirect_to = t.get_absolute_url() + "?previous=parent"

        elif value == None:
            # User is skipping this question.
            answered_by_tasks = []

        else:
            # User selects existing Tasks.
            # Validate that the tasks are of the right type (module) and
            # the user has read access.
            answered_by_tasks = [
                Task.objects.get(id=int(item))
                for item in value.split(',')
                ]
            for t in answered_by_tasks:
                if t.module != q.answer_type_module or not t.has_read_priv(request.user):
                    raise ValueError("invalid task ID")
            if q.spec["type"] == "module" and len(answered_by_tasks) != 1:
                raise ValueError("did not provide exactly one task ID")
        
        value = None
        answered_by_file = None

    elif q.spec["type"] == "file" and not cleared:
        # Don't save the File into the stored_value field in the database.
        # Instead put it in answered_by_file. value may be None if the user
        # is skipping the question.
        answered_by_file = value
        value = None

    else:
        answered_by_file = None

    # Create a new TaskAnswerHistory record, if the answer is actually changing.
    if cleared:
        # Clear the answer.
        question.clear_answer(request.user)
        instrumentation_event_type = "clear"
    else:
        # Save the answer.
        had_answer = question.has_answer()
        if question.save_answer(
            value, answered_by_tasks, answered_by_file,
            request.user, "web",
            skipped_reason=skipped_reason, unsure=unsure):

            # The answer was changed (not just saved as a new answer).
            if request.POST.get("method") == "skip":
                instrumentation_event_type = "skip"
            elif had_answer:
                instrumentation_event_type = "change"
            else: # is a new answer
                instrumentation_event_type = "answer"
        else:
            instrumentation_event_type = "keep"

    # Add instrumentation event.
    # --------------------------
    # How long was it since the question was initially viewed? That gives us
    # how long it took to answer the question.
    i_task_question_view = InstrumentationEvent.objects\
        .filter(user=request.user, event_type="task-question-show", task=task, question=q)\
        .order_by('event_time')\
        .first()
    i_event_value = (timezone.now() - i_task_question_view.event_time).total_seconds() \
        if i_task_question_view else None
    # Save.
    InstrumentationEvent.objects.create(
        user=request.user,
        event_type="task-question-" + instrumentation_event_type,
        event_value=i_event_value,
        module=task.module,
        question=q,
        project=task.project,
        task=task,
        answer=question,
        extra={
            "answer_value": value,
        }
    )

    # Form a JSON response to the AJAX request and indicate the
    # URL to redirect to, to load the next question.
    response = JsonResponse({ "status": "ok", "redirect": redirect_to })

    # Return the response.
    return response

@task_view
def show_question(request, task, answered, context, q):
    # Let's talk about where the data is for this question. The 'q'
    # argument is a ModuleQuestion instance. The YAML data associated
    # with this question (like id, type, prompt, etc.) are stored in
    #   q.spec
    # which is a Python dict holding the exact same information as
    # in the part of the YAML file for this question.
    #
    # q.module points to the Module it is contained in (i.e. the YAML file
    # it is contained in). q.module is a Module instance, and the
    # YAML data associated with that Module (id, output documents, etc)
    # is stored in
    #  q.module.spec
    # which is a Python dict holding the exact same information as in
    # the module YAML file on disk *except* for the questions array,
    # because that data is stored in the ModuleQuestions instances.
    #
    # q.module.app points to the AppVersion instance for the compliance
    # app that contains the module that contains the question. The
    # AppVersion stores the app.yaml data in two places. One place is
    #   q.module.app.catalog_metadata
    # which is a Python dict that holds the YAML data found in the
    # "catalog" key in the app.yaml file.
    #
    # The other data in app.yaml is used to define the Module named
    # "app" within the compliance app. Therefore it is found in
    #   q.module.app.modules.get(module_name="app").spec
    # which is a Python dict similar to q.module.spec.

    # If this question cannot currently be answered (i.e. dependencies are unmet),
    # then redirect away from this page. If the user is allowed to use the authoring
    # tool, then allow seeing this question so they can edit all questions.
    authoring_tool_enabled = task.module.is_authoring_tool_enabled(request.user)
    can_upgrade_app = task.module.app.has_upgrade_priv(request.user)

    is_answerable = (((q not in answered.unanswered) or (q in answered.can_answer)) and (q.key not in answered.was_imputed))
    if not is_answerable and not authoring_tool_enabled:
        return HttpResponseRedirect(task.get_absolute_url())

    # Is there a TaskAnswer for this yet?
    taskq = TaskAnswer.objects.filter(task=task, question=q).first()

    # Display requested question.

    # Is there an answer already? (If this question isn't answerable, i.e. if we're
    # only here because the user is using the authoring tool, then there is no
    # real answer to load.)
    answer = None
    if taskq and is_answerable:
        answer = taskq.get_current_answer()
        if answer and answer.cleared:
            # If the answer is cleared, treat as if it had not been answered.
            answer = None

    # For "module"-type questions, get the Module instance of the tasks that can
    # be an answer to this question, and get the existing Tasks that the user can
    # choose as an answer.
    answer_module = q.answer_type_module
    answer_tasks = []
    if answer_module:
        # The user can choose from any Task instances they have read permission on
        # and that are of the correct Module type.
        answer_tasks = Task.get_all_tasks_readable_by(request.user, recursive=True)\
            .filter(module=answer_module)

        # Annotate the instances with whether the user also has write permission.
        for t in answer_tasks:
            t.can_write = t.has_write_priv(request.user)

        # Sort the instances:
        #  first: the current answer, if any
        #  then: tasks defined in the same project as this task
        #  later: tasks defined in projects in the same folder as this task's project
        #  last: everything else by reverse update date
        now = timezone.now()
        current_answer = answer.answered_by_task.first() if answer else None
        answer_tasks = sorted(answer_tasks, key = lambda t : (
            not (t == current_answer),
            not (t.project == task.project),
            not (set(t.project.contained_in_folders.all()) & set(task.project.contained_in_folders.all())),
            now-t.updated,
            ))

    # Add instrumentation event.
    # How many times has this question been shown?
    i_prev_view = InstrumentationEvent.objects\
        .filter(user=request.user, event_type="task-question-show", task=task, question=q)\
        .order_by('-event_time')\
        .first()
    # Save.
    InstrumentationEvent.objects.create(
        user=request.user,
        event_type="task-question-show",
        event_value=(i_prev_view.event_value+1) if i_prev_view else 1,
        module=task.module,
        question=q,
        project=task.project,
        task=task,
        answer=taskq,
    )

    # Indicate for the InstrumentQuestionPageLoadTimes middleware that this is
    # a question page load.
    request._instrument_page_load = {
        "event_type": "task-question-request-duration",
        "module": task.module,
        "question": q,
        "project": task.project,
        "task": task,
        "answer": taskq,
    }

    # Construct the page.
    def render_markdown_value(template, output_format, reference, **kwargs):
        if not isinstance(template, str):
            raise ValueError(reference + " is not a string")
        try:
            return module_logic.render_content({
                    "template": template,
                    "format": "markdown",
                },
                answered,
                output_format,
                reference,
                **kwargs
            )
        except Exception as e:
            error = "There was a problem rendering {} for this question: {}.".format(reference, str(e))
            if output_format == "html":
                import html
                error = "<p class='text-danger'>" + html.escape(error) + "</p>\n"
            return error
    def render_markdown_field(field, output_format, **kwargs):
        template = q.spec.get(field)
        if not template:
            return None
        return render_markdown_value(template, output_format, field)

    # Get any existing answer for this question.
    existing_answer = None
    if answer:
        existing_answer = answer.get_value()

        # For longtext questions, because the WYSIWYG editor is initialized with HTML,
        # render the value as HTML.
        if existing_answer and q.spec["type"] == "longtext":
            import commonmark
            existing_answer = commonmark.HtmlRenderer({ "safe": True }).render(commonmark.Parser().parse(existing_answer))

    # For file-type questions that have been answered, render the existing
    # answer so that we don't need redundant logic for showing a thumbnail
    # and providing a download link.
    answer_rendered = None
    if taskq and taskq.question.spec["type"] == "file" and answer:
        from .module_logic import TemplateContext, RenderedAnswer, HtmlAnswerRenderer
        tc = TemplateContext(answered, HtmlAnswerRenderer(show_metadata=False))
        ra = RenderedAnswer(task, taskq.question, True, answer, existing_answer, tc)
        answer_rendered = ra.__html__()

    # What's the title/h1 of the page and the rest of the prompt? Render the
    # prompt field. If it starts with a paragraph, turn that paragraph into
    # the title.
    title = q.spec["title"]
    prompt = render_markdown_field("prompt", "html")
    m = re.match(r"^<p>([\w\W]*?)</p>\s*", prompt)
    if m:
        title = m.group(1)
        prompt = prompt[m.end():]

    # Get a default answer for this question. Render Jinja2 template, but don't turn
    # Markdown into HTML for plain text fields. For longtext fields, turn it into
    # HTML because the WYSIWYG editor is initialized with HTML.
    default_answer = render_markdown_field("default",
        "text" if q.spec["type"] != "longtext" else "html",
        demote_headings=False)

    ###############################################################################
    # BLOCK CREATE task_progress_project_list
    #
    # TODO: REFACTOR INTO INDIVIDUAL ROUTE
    # Get higher level context history for this task
    # This code largely repeated from siteapp > views > project page
    #
    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    # Better to refactor context into its own view
    # instead of recreating from inside this question
    ###############################################################################

    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    root_task_answers = task.project.root_task.get_answers().with_extended_info()
    task_progress_project_list = []
    # current_mq_group = ""
    current_group = None

    # Check if this user has authorization to start tasks in this Project.
    can_start_task = task.project.can_start_task(request.user)

    # Collect all of the questions and answers, i.e. the sub-tasks, that we'll display.
    # Create a "question" record for each question that is displayed by the template.
    # For module-set questions, create one record to start new entries and separate
    # records for each answered module.
    from collections import OrderedDict
    questions = OrderedDict()
    can_start_any_apps = False

    # for item in root_task_answers.answertuples.items():
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
            icon = task.project.root_task.get_static_asset_image_data_url(mq.spec["icon"], 75)
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
                # "discussions": [d for d in discussions if d.attached_to.task == module_answers.task],
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

        if questions.get(mq.id) and 'task' in questions[mq.id]:
            # print("\nquestions[mq.id]['task'].id", dir(questions[mq.id]['task']))
            task_link = "/tasks/{}/{}".format(questions[mq.id]['task'].id, "start")
            task_id = questions[mq.id]['task'].id
            task_started = questions[mq.id]['task'].is_started()
            task_answered = questions[mq.id]['task'].is_finished()
        else:
            # Question not started
            # TODO: Need better match than "/TODO"
            task_link = "/TODO"
            task_id = None
            task_started = False
            task_answered = False

        tasks_in_group = {
            "id": mq.spec.get('id'),
            "module_id": mq.spec.get('module-id'),
            "group": mq.spec.get('group'),
            "title": mq.spec.get('title'),
            "type": mq.spec.get('type'),
            "link": task_link,
            "task_id": task_id,
            "task_started": task_started,
            "task_answered": task_answered,
            }
        task_progress_project_list.append(tasks_in_group)

        # Notes on what comes next, how we identify the current_group we are in based on the question.
        # We need to make sure we are comparing module-id rather than id b/c the question.module-id
        # does not have to be the same as the question.module.id.
        # The original comparison (below) works only when the app.yaml question `id` and `module-id` are identical: 
        #
        #       if mq.spec.get('id') == task.module.spec.get('id'): #orig
        #
        # But the above fails when the`module-id` differs from the `id` which is permitted.
        #
        # To address the shortcoming of the above original test, we remember that the id of the module does not need to be the same as the "module-id". We need to do some walking in the relationship to compare
        # apples to apple. For the `mq` (module question), we need to go to `answer_type_module` and get the `module_name`. For the `Task`, we need to
        # go to the `module` and the `spec` to get the `id`).
        if mq.answer_type_module.module_name == task.module.spec.get('id'):
            current_group = mq.spec.get('group')
    ###############################################################################
    # END BLOCK task_progress_project_list
    ###############################################################################

    # get context of questions in module
    context_sorted = module_logic.get_question_context(answered, q)
    # determine next linear question
    current_q_index = next((index for (index, d) in enumerate(context_sorted) if d["is_this_question"] == True), None)
    if current_q_index < len(context_sorted) - 1:
        next_linear_question = context_sorted[current_q_index + 1]
    else:
        next_linear_question = None


    context.update({
        "header_col_active": "start" if (len(answered.as_dict()) == 0 and q.spec["type"] == "interstitial") else "questions",
        "q": q,
        "title": title,
        "prompt": prompt,
        "placeholder_answer": render_markdown_field("placeholder", "text") or "", # Render Jinja2 template but don't turn Markdown into HTML.
        "example_answers": [render_markdown_value(ex.get("example", ""), "html", "example {}".format(i+1)) for i, ex in enumerate(q.spec.get("examples", []))],
        "reference_text": render_markdown_field("reference_text", "html"),
        "history": taskq.get_history() if taskq else None,
        "answer_obj": answer,
        "answer": existing_answer,
        "answer_rendered": answer_rendered,
        "default_answer": default_answer,
        "hidden_button_ids": q.module.app.modules.get(module_name="app").spec.get("hidden-buttons", []),
        "can_review": task.has_review_priv(request.user),
        "review_choices": TaskAnswerHistory.REVIEW_CHOICES,
        "discussion": Discussion.get_for(taskq.task.project.organization, taskq) if taskq else None,
        "show_discussion_members_count": True,

        "answer_module": answer_module,
        "answer_tasks": answer_tasks,
        "answer_tasks_show_user": len([ t for t in answer_tasks if t.editor != request.user ]) > 0,

        "context": context_sorted,
        "next_linear_question": next_linear_question,

        # task_progress_project_list parameters
        "root_task_answers": root_task_answers,
        "task_progress_project_list": task_progress_project_list,
        "current_group": current_group,

        # Helpers for showing date month, day, year dropdowns, with
        # localized strings and integer values. Default selections
        # are done in the template & client-side so that we can use
        # the client browser's timezone to determine the current date.
        "date_l8n": lambda : {
            "months": [
                (timezone.now().replace(2016,m,1).strftime("%B"), m)
                for m in range(1, 12+1)],
            "days": [
                d
                for d in range(1, 31+1)],
            "years": [
                y
                for y in reversed(range(timezone.now().year-100, timezone.now().year+101))],
        },

        "is_answerable": is_answerable, # only false if authoring tool is enabled, otherwise this page is not renderable
        "can_upgrade_app": can_upgrade_app,
        "authoring_tool_enabled": authoring_tool_enabled,
        "is_question_page": True,
        "project_form": ProjectForm(request.user),
    })
    return render(request, "question.html", context)

@task_view
def task_finished(request, task, answered, context, *unused_args):
    # All of the questions in this task have been answered. Review the
    # answers and show the task's output documents.

    # Add instrumentation event.
    # Has the user been here before?
    i_task_done = InstrumentationEvent.objects\
        .filter(user=request.user, event_type="task-done", task=task)\
        .exists()
    # How long since the task was created?
    i_task_create = InstrumentationEvent.objects\
        .filter(user=request.user, event_type="task-create", task=task)\
        .first()
    i_event_value = (timezone.now() - i_task_create.event_time).total_seconds() \
        if i_task_create else None
    # Save.
    InstrumentationEvent.objects.create(
        user=request.user,
        event_type="task-done" if not i_task_done else "task-review",
        event_value=i_event_value,
        module=task.module,
        project=task.project,
        task=task,
    )

    ###############################################################################
    # BLOCK CREATE task_progress_project_list
    #
    # TODO: REFACTOR INTO INDIVIDUAL ROUTE
    # Get higher level context history for this task
    # This code largely repeated from siteapp > views > project page
    #
    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    # Better to refactor context into its own view
    # instead of recreating from inside this question
    ###############################################################################

    # Pre-load the answers to project root task questions and impute answers so
    # that we know which questions are suppressed by imputed values.
    root_task_answers = task.project.root_task.get_answers().with_extended_info()
    task_progress_project_list = []
    # current_mq_group = ""
    current_group = None
    next_group = None
    next_module = None
    next_module_spec = None

    # Check if this user has authorization to start tasks in this Project.
    can_start_task = task.project.can_start_task(request.user)

    # Collect all of the questions and answers, i.e. the sub-tasks, that we'll display.
    # Create a "question" record for each question that is displayed by the template.
    # For module-set questions, create one record to start new entries and separate
    # records for each answered module.
    from collections import OrderedDict
    questions = OrderedDict()
    can_start_any_apps = False

    # for item in root_task_answers.answertuples.items():
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
            icon = task.project.root_task.get_static_asset_image_data_url(mq.spec["icon"], 75)
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
                # "discussions": [d for d in discussions if d.attached_to.task == module_answers.task],
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

        if 'task' in questions[mq.id]:
            # print("\nquestions[mq.id]['task'].id", dir(questions[mq.id]['task']))
            task_link = "/tasks/{}/{}".format(questions[mq.id]['task'].id, "start")
            task_id = questions[mq.id]['task'].id
            task_started = questions[mq.id]['task'].is_started()
            task_answered = questions[mq.id]['task'].is_finished()
        else:
            # Question not started
            # TODO: Need better match than "/TODO"
            task_link = "/TODO"
            task_id = None
            task_started = False
            task_answered = False

        tasks_in_group = {
            "id": mq.spec.get('id'),
            "module_id": mq.spec.get('module-id'),
            "group": mq.spec.get('group'),
            "title": mq.spec.get('title'),
            "type": mq.spec.get('type'),
            "link": task_link,
            "task_id": task_id,
            "task_started": task_started,
            "task_answered": task_answered,
            }
        task_progress_project_list.append(tasks_in_group)
        if mq.spec.get('id') == task.module.spec.get('id'):
            current_group = mq.spec.get('group')
        elif current_group is not None and next_group is None:
            # Determine next group after current group
            next_group = mq.spec.get('group')
            next_module = mq
            next_module_spec = mq.spec
    ###############################################################################
    # END BLOCK task_progress_project_list
    ###############################################################################

    # Construct the page.

    top_of_page_output = None
    outputs = task.render_output_documents(answered)
    for i, output in enumerate(outputs):
        if output.get("display") == "top":
            top_of_page_output = output
            del outputs[i]

    context.update({
        "had_any_questions": len(set(answered.as_dict()) - answered.was_imputed) > 0,
        "top_of_page_output": top_of_page_output,
        "outputs": outputs,
        "all_answers": answered.render_answers(show_metadata=True, show_imputed_nulls=False),
        "can_review": task.has_review_priv(request.user),
        "project": task.project,
        "can_upgrade_app": task.project.root_task.module.app.has_upgrade_priv(request.user),
        "authoring_tool_enabled": task.project.root_task.module.is_authoring_tool_enabled(request.user),

        # task_progress_project_list parameters
        "root_task_answers": root_task_answers,
        "task_progress_project_list": task_progress_project_list,
        "current_group": current_group,
        "context": module_logic.get_question_context(answered, None),
        "next_group": next_group,
        "next_module": next_module,
        "next_module_spec": next_module_spec,
        # "context": context,
        "project_form": ProjectForm(request.user, initial={'portfolio': task.project.portfolio.id}) if task.project.portfolio else ProjectForm(request.user)

    })
    return render(request, "task-finished.html", context)

@task_view
def download_answer_file(request, task, answered, context, q, history_id):
    # Get the TaskAnswerHistory object referenced in the URL.
    tah = get_object_or_404(TaskAnswerHistory, id=history_id, taskanswer__task=task, taskanswer__question=q)

    # It should have a file question and a file answer.
    if q.spec["type"] != "file": raise Http404()
    if not tah.answered_by_file.name: raise Http404()

    # Get the Django File instance. If ?thumbnail=1 is passed, retreive the thumbnail
    # if it exists.
    blob = tah.answered_by_file
    if request.GET.get("thumbnail"):
        tah.get_value() # populate lazy-created thumbnail
        if not tah.thumbnail.name: raise Http404()
        blob = tah.thumbnail

    # Get the dbstorage.models.StoredFile instance which holds
    # an auto-detected mime type.
    from dbstorage.models import StoredFile
    sf = StoredFile.objects.only("mime_type").get(path=blob.name)

    # Construct the response. The file content is untrusted, so it must
    # not be served as an inline resource from our domain unless it is
    # an image, which browsers won't execute.
    if sf.mime_type and sf.mime_type.startswith("image/"):
        mime_type = sf.mime_type
        disposition = "inline"
    else:
        mime_type = "application/octet-stream"
        disposition = "attachment"

    import os.path
    resp = HttpResponse(blob, content_type=mime_type)
    resp['Content-Disposition'] = disposition + '; filename=' + os.path.basename(blob.name)


    # Browsers may guess the MIME type if it thinks it is wrong. Prevent
    # that so that if we are forcing application/octet-stream, it
    # doesn't guess around it and make the content executable.
    resp['X-Content-Type-Options'] = 'nosniff'

    # Browsers may still allow HTML to be rendered in the browser. IE8
    # apparently rendered HTML in the context of the domain even when a
    # user clicks "Open" in an attachment-disposition response. This
    # prevents that. Doesn't seem to affect anything else (like images).
    resp['X-Download-Options'] = 'noopen'

    return resp

@task_view
def download_module_output(request, task, answered, context, question, document_id, download_format):
    if document_id in (None, ""):
        raise Http404()
    try:
        blob, filename, mime_type= task.download_output_document(document_id, download_format, answers=answered)
    except ValueError:
        raise Http404()

    resp = HttpResponse(blob, mime_type)
    resp['Content-Disposition'] = 'inline; filename=' + filename
    return resp

@login_required
def instrumentation_record_interaction(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # Get event variables.
    
    task = get_object_or_404(Task, id=request.POST["task"])
    if not task.has_read_priv(request.user):
        return HttpResponseForbidden()

    from django.core.exceptions import ObjectDoesNotExist
    try:
        question = task.module.questions.get(id=request.POST.get("question"))
    except ObjectDoesNotExist:
        return HttpResponseForbidden()

    answer = TaskAnswer.objects.filter(task=task, question=question).first()

    # We're recording the *first* interaction, so we'll
    # stop if an interaction has already been recorded.

    if InstrumentationEvent.objects.filter(
        user=request.user, event_type="task-question-interact-first",
        task=task, question=question).exists():
        return HttpResponse("ok")

    # When was the question first viewed? We'll use that
    # to compute the time to first interaction.

    i_task_question_view = InstrumentationEvent.objects\
        .filter(user=request.user, event_type="task-question-show", task=task, question=question)\
        .order_by('event_time')\
        .first()
    event_value = (timezone.now() - i_task_question_view.event_time).total_seconds() \
        if i_task_question_view else None

    # Save.

    InstrumentationEvent.objects.create(
        user=request.user,
        event_type="task-question-interact-first",
        event_value=event_value,
        module=task.module,
        question=question,
        project=task.project,
        task=task,
        answer=answer,
    )

    return HttpResponse("ok")

def authoring_tool_auth(f):
    def g(request):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        # Get the task and question and check permissions.

        task = get_object_or_404(Task, id=request.POST["task"])
        if not task.has_write_priv(request.user):
            return HttpResponseForbidden()
        if not task.module.is_authoring_tool_enabled(request.user):
            return HttpResponseForbidden()

        # Run inner function.
        return f(request, task)

    return g

@login_required
@transaction.atomic
def authoring_create_q(request):
    from guidedmodules.models import AppSource
    from collections import OrderedDict

    new_q_appsrc = AppSource.objects.get(slug="govready-q-files-stubs")

    # Get the values from submitted form
    new_q = OrderedDict()
    for field in (
        "q_slug", "title", "short_description", "category"):
        value = request.POST.get(field, "").strip()
        # Example how we can test values and make changes
        if value:
            if field in ("min", "max"):
                new_q[field] = int(value)
            elif field == "protocol":
                # The protocol value is given as a space-separated list of
                # of protocols.
                new_q[field] = re.split(r"\s+", value)
            else:
                new_q[field] = value

    # Use stub_app to publish our new app
    try:
        appver = new_q_appsrc.add_app_to_catalog("stub_app" )
        # Update app details
        appver.appname = new_q["title"]
        appver.catalog_metadata["title"] = new_q["title"]
        appver.catalog_metadata["description"]["short"] = new_q['short_description']
        appver.catalog_metadata["category"] = new_q["category"]
        # appver.spec.introduction.template = new_q['short_description']
        appver.save()
    except Exception as e:
        raise

    from django.contrib import messages
    messages.add_message(request, messages.INFO, 'New Project "{}" added into the catalog.'.format(new_q["title"]))

    return JsonResponse({ "status": "ok", "redirect": "/store" })

@login_required
@transaction.atomic
def upgrade_app(request):
    # Upgrade an AppVersion in place by reloading all of its Modules from the
    # app's current definition in its AppSource. This should mainly be used
    # for compliance app authors during the app authoring process. All projects
    # that are using the AppVersion will be affected.
    #
    # TODO: We should have a different sort of upgrade when instead of updating
    # an AppVersion in-place, we simply re-link this Project to a newer AppVersion
    # already in the database.

    # Check that the user is permitted to do so.
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    from .models import AppVersion
    appver = get_object_or_404(AppVersion, id=request.POST["app"])
    if not appver.has_upgrade_priv(request.user):
        return HttpResponseForbidden()

    from .app_loading import load_app_into_database, AppImportUpdateMode, ModuleDefinitionError, IncompatibleUpdate
    with appver.source.open() as store:
            # Load app.
            try:
                app = store.get_app(appver.appname)
            except ValueError as e:
                return JsonResponse({ "status": "error", "message": str(e) })

            # What update mode? By default, only allow compatible updates.
            mode = AppImportUpdateMode.CompatibleUpdate

            # If using authoring tools, allow forced updates.
            if appver.is_authoring_tool_enabled(request.user) \
                and request.POST.get("force") == "true":
                mode = AppImportUpdateMode.ForceUpdate

            # Import.
            try:
                load_app_into_database(app, mode, appver)
            except (ModuleDefinitionError, IncompatibleUpdate) as e:
                return JsonResponse({ "status": "error", "message": str(e) })

    # Since ModuleQuestions may have changed...
    from .module_logic import clear_module_question_cache
    clear_module_question_cache()

    # Since impute conditions, output documents, and other generated
    # data may have changed, clear all cached Task state.
    Task.clear_state(Task.objects.filter(module__app=appver))

    from django.contrib import messages
    messages.add_message(request, messages.INFO, 'App upgraded.')

    return JsonResponse({ "status": "ok" })

@authoring_tool_auth
@transaction.atomic
def authoring_download_app(request, task):
    question = get_object_or_404(ModuleQuestion, module=task.module, key=request.POST['question'])

    # Download current questionnaire.
    print("In `authoring_download_app` and attempting to download question/app")
    try:
        questionnaire_yaml = question.module.serialize()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not download YAML file: " + str(e) })

    # Clear cache...
    from .module_logic import clear_module_question_cache
    clear_module_question_cache()

    # ////////////////////
    # GET DOWNLOAD TO WORK
    # mime_type = "text/x-yaml"
    # disposition = "inline"
    # resp = HttpResponse(questionnaire_yaml, content_type=mime_type)
    # resp['Content-Disposition'] = disposition + '; filename=' + "q-file.yaml"

    # # Browsers may guess the MIME type if it thinks it is wrong. Prevent
    # # that so that if we are forcing application/octet-stream, it
    # # doesn't guess around it and make the content executable.
    # resp['X-Content-Type-Options'] = 'nosniff'

    # # Browsers may still allow HTML to be rendered in the browser. IE8
    # # apparently rendered HTML in the context of the domain even when a
    # # user clicks "Open" in an attachment-disposition response. This
    # # prevents that. Doesn't seem to affect anything else (like images).
    # resp['X-Download-Options'] = 'noopen'

    # return resp
    # ////////////////////

    # Return status. The browser will reload/redirect --- if the question key
    # changed, this sends the new key.
    return JsonResponse({ "status": "ok",
                          "data": questionnaire_yaml,
                          "redirect": task.get_absolute_url_to_question(question)
                        })

@authoring_tool_auth
@transaction.atomic
def authoring_download_app_project(request, task):
    # Download a project
#    print("Calling to download task: {}".format(task))
    # Get project that this Task is a part of
    project_obj = task.project
#    print("project is {}".format(project_obj))

    # Get module that this task is answering
    # module_obj = task.module
    # print("module_obj is {}".format(module_obj))
    # print("module_obj.spec is {}".format(module_obj.spec))
    # print("module.serialize: ")
    # print("{}".format(module_obj.serialize()))
    # Recreate the yaml of the module (e.g, app-project)
#    print("text {}".format(task.module.serialize()))

    # Download current project_app (.e.g, module) in use.
#    print("In `authoring_download_app_project` and attempting to download project-app")
    try:
        module_yaml = task.module.serialize()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not download YAML file: " + str(e) })

    # Do I need something similar?
    # Clear cache...
    # from .module_logic import clear_module_question_cache
    # clear_module_question_cache()

    # As a project app, There also exists:
    # - asset directory with assets
    # - state information

    # Get the app (AppVersion) connected to this module
    # appversion_obj =  module_obj.app
    # print("appversion_obj is {}".format(appversion_obj))
    # print("appversion_obj version_name is {}".format(appversion_obj.version_name))
    # print("appversion_obj version_number is {}".format(appversion_obj.version_number))

    # Download current questionnaire.

    # How do I dump the entire app?
    return JsonResponse({ "status": "ok",
                          "data": module_yaml,
                        })

@authoring_tool_auth
def authoring_new_question(request, task):
    # Find a new unused question identifier.
    ids_in_use = set(task.module.questions.values_list("key", flat=True))
    key = 0
    while "q" + str(key) in ids_in_use: key += 1
    key = "q" + str(key)

    # Get the highest definition_order in use so far.
    definition_order = max([0] + list(task.module.questions.values_list("definition_order", flat=True))) + 1

    # Make a new spec.
    if task.module.spec.get("type") == "project":
        # Probably in app.yaml
        spec = {
            "id": key,
            "type": "module",
            "title": "New Question Title",
            "protocol": ["choose-a-module-or-enter-a-protocol-id"],
        }
        # # Make a new modular spec
        # mspec = {"id": key,
        #          "title": key.replace("_"," ").title(),
        #          "questions": [
        #             {"id": "mqo",
        #              "type": "text",
        #              "title": "New Question Title",
        #              "prompt": "Enter some text.",
        #              },
        #          ],
        #          "output": []
        #          }
        # # Make a new modular instance
        # new_module = Module(
        #     source=task.module.app.source,
        #     app=task.module.app,
        #     module_name=key,
        #     spec=mspec
        # )
        # new_module.save()

        # spec = {
        #    "id": key,
        #    "type": "module",
        #    "title": "New Question Title",
        #    "module-id": key,
        # }

        # # Make a new question instance.
        # question = ModuleQuestion(
        #     module=task.module,
        #     key=key,
        #     definition_order=definition_order,
        #     spec=spec
        #     )
        # question.save()

    else:
        spec = {
            "id": key,
            "type": "text",
            "title": "New Question Title",
            "prompt": "Enter some text.",
        }

        # Make a new question instance.
        question = ModuleQuestion(
            module=task.module,
            key=key,
            definition_order=definition_order,
            spec=spec
            )
        question.save()

    # Write to disk. Write updates to disk if developing on local machine
    # with local App Source
    try:
        question.module.serialize_to_disk()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not update local YAML file: " + str(e) })

    # Clear cache...
    from .module_logic import clear_module_question_cache
    clear_module_question_cache()

    # Return status. The browser will reload/redirect --- if the question key
    # changed, this sends the new key.
    return JsonResponse({ "status": "ok", "redirect": task.get_absolute_url_to_question(question) })

@authoring_tool_auth
@transaction.atomic
def authoring_edit_question(request, task):

    question = get_object_or_404(ModuleQuestion, module=task.module, key=request.POST['question'])

    # Delete the question?
    if request.POST.get("delete") == "1":
        try:
            question.delete()
            return JsonResponse({ "status": "ok", "redirect": task.get_absolute_url() })
        except Exception as e:
            # The only reason it would fail is a protected foreign key.
            return JsonResponse({ "status": "error", "message": "The question cannot be deleted because it has already been answered." })

    # Update the question...

    # Update the key.
    question.key = request.POST['newid']

    try:

        # Create the spec dict, starting with the standard fields.
        # Most fields are strings and need no extra processing but
        # some need to be parsed.
        from collections import OrderedDict
        spec = OrderedDict()
        spec["id"] = request.POST['newid']
        for field in (
            "title", "prompt", "type", "placeholder", "default", "help",
            "choices", "min", "max", "file-type", "protocol"):
            value = request.POST.get(field, "").strip()
            if value:
                if field in ("min", "max"):
                    spec[field] = int(value)
                elif field == "choices":
                    spec[field] = ModuleQuestion.choices_from_csv(value)
                elif field == "protocol" and request.POST.get("module-id") != "/app/":
                    # The protocol value is only valid if "/app/" was chosen
                    # in the UI as the module type. It wasn't, so skip it.
                    continue
                elif field == "protocol":
                    # The protocol value is given as a space-separated list of
                    # of protocols.
                    spec[field] = re.split(r"\s+", value)
                else:
                    spec[field] = value

        # For module-type questions the "module-id" form field gives a Module instance
        # ID, which we need to set in the Question.answer_type_module field as well
        # as in the Question.spec["module-id"] field for validation and serialization
        # to YAML on disk. The value "/app/" is used when a protocol ID is specified
        # instead (which is handled above).
        question.answer_type_module = None
        if spec["type"] in ("module", "module-set") \
         and request.POST.get("module-id") not in (None, "", "/app/"):
            m = Module.objects.get(id=request.POST["module-id"])
            if m not in question.module.get_referenceable_modules():
                raise ValueError("The selected module is not valid.")
            question.answer_type_module = m
            spec["module-id"] = question.module.getReferenceTo(m)

        # Add impute conditions, which are spread across an arbitrary number of
        # triples of fields named like impute_condition_###_{condition,value,valuemode}.
        impute_condition_field_numbers = set()
        for key, value in request.POST.items():
            m = re.match(r"^impute_condition_(\d+)_(condition|value|valuemode)$", key)
            if m: impute_condition_field_numbers.add(int(m.group(1)))
        for impute_number in sorted(impute_condition_field_numbers):
            key = "impute_condition_" + str(impute_number) + "_"
            impute = OrderedDict()
            impute["condition"] = request.POST.get(key + "condition", "")
            if impute["condition"].strip() == "": continue # skip if the expression is empty
            impute["value"] = request.POST.get(key + "value", "")
            impute["value-mode"] = request.POST.get(key + "valuemode", "")
            if impute["value-mode"] in (None, "raw"):
                # The default value mode is a raw value, which
                # we must parse from the form string value.
                del impute["value-mode"]
                try:
                    import rtyaml
                    impute["value"] = rtyaml.load(impute["value"])
                except ValueError as e:
                    raise ValueError("Error in impute condition %s value: %s" %
                        (impute_number, str(e)))
            spec.setdefault("impute", []).append(impute)

        # If additional JSON spec data is provided, add it.
        if request.POST.get("spec", "").strip():
            import rtyaml
            spec.update(rtyaml.load(request.POST["spec"]))

        # Validate.
        from .validate_module_specification import validate_question
        spec = validate_question(question.module.spec, spec)

        # As in app loading, rewrite this...
        if question.answer_type_module:
            spec["module-id"] = question.answer_type_module.id

    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })

    # Save.
    question.spec = spec
    question.save()

    # Write to disk. Errors writing should not be suppressed because
    # saving to disk is a part of the contract of how app editing works.
    try:
        question.module.serialize_to_disk()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not update local YAML file: " + str(e) })

    # Clear cache...
    from .module_logic import clear_module_question_cache
    clear_module_question_cache()

    # Return status. The browser will reload/redirect --- if the question key
    # changed, this sends the new key.
    return JsonResponse({ "status": "ok", "redirect": task.get_absolute_url_to_question(question) })

@authoring_tool_auth
@transaction.atomic
def authoring_edit_module(request, task):
    try:
        # Update the module.
        import rtyaml
        spec = rtyaml.load(request.POST["spec"])

        # Validate.
        from .validate_module_specification import validate_module
        spec = validate_module(spec, None, is_authoring_tool=True)
    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })

    # Save.
    task.module.spec = spec
    task.module.save()

    # Update the compliance app's catalog_metadata if the user is
    # editing a root_task.
    if task.module.module_name == "app":
        import rtyaml
        task.module.app.catalog_metadata = rtyaml.load(request.POST["catalog_metadata"])
        task.module.app.save()

    # Write to disk. Errors writing should not be suppressed because
    # saving to disk is a part of the contract of how app editing works.
    try:
        task.module.serialize_to_disk()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not update local YAML file: " + str(e) })

    # Clear cache...
    from .module_logic import clear_module_question_cache
    clear_module_question_cache()

    # Return status. The browser will reload/redirect --- if the question key
    # changed, this sends the new key.
    return JsonResponse({ "status": "ok", "redirect": task.get_absolute_url() })

@login_required
@transaction.atomic
def delete_task(request):
    # Mark a Task as deleted and un-link it from any questions it
    # answers by saving new answers with the Task removed. Only
    # Project admins can delete tasks. It's not a destructive
    # operation at the database level, but it does cause the Task
    # to become inaccessible.

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    task = get_object_or_404(Task, id=request.POST["id"])
    if not task.has_delete_priv(request.user):
        return HttpResponseForbidden()

    # Don't allow root tasks to be deleted this way.
    if task is task.project.root_task:
        return HttpResponseForbidden()

    if task.deleted_at is None:
        # Mark.
        task.deleted_at = timezone.now()
        task.save(update_fields=["deleted_at"])

        # Update answers that this Task is an answer to with the same
        # value but missing this Task.
        for ans in task.is_answer_to.all():
            if not ans.is_latest(): continue # only update if we're looking at the current answer to a question
            ans.taskanswer.save_answer(
                None, # if it had a Task answer, it can't have had stored_value
                set(ans.answered_by_task.all()) - { task }, # remove the task
                None, # if it had a Task answer, it can't have had an answer file
                request.user,
                "del", # save method - unique to this operation because it violates normal auth checks on modifying tasks
                skipped_reason=ans.skipped_reason, # preserve this
                unsure=ans.unsure, # preserve this
            )

    return HttpResponse("ok")

@login_required
def get_task_timetamp(request):
    # Get the 'updated' timestamp on the task and if 'get_changes_since'
    # is passed, scan for new answers within this project and return a
    # summary of the changes.

    # Check access.
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    task = get_object_or_404(Task, id=request.POST["id"])
    if not task.has_read_priv(request.user):
        return HttpResponseForbidden()

    # Form response.
    ret = {
        "timestamp": task.updated.timestamp()
    }

    # If get_changes_since is provided and it doesn't match the current
    # timestamp of the task, scan the project recursively for new answers
    # since the given time.
    try:
        get_changes_since = float(request.POST.get("get_changes_since"))
    except:
        get_changes_since = None
    if get_changes_since and get_changes_since != ret["timestamp"]:

        def summarize_task_changes(task, path, seen_tasks):
            if task in seen_tasks:
                # Prevent infinite recursion. If we've done
                # this task already, pretend is has no changes
                # on later visits.
                return []
            seen_tasks.add(task)

            # What are the new answers?
            ret = []
            all_authors = set()
            for q, a in task.get_current_answer_records():
                # This question is not yet answered.
                if a is None:
                    continue

                # This question has a new answer.
                if a.created.timestamp() > get_changes_since:
                    # Construct string for the author.
                    author = "{} (using {})".format(
                        str(a.answered_by),
                        a.get_answered_by_method_display()
                    )
                    all_authors.add(author)

                    # Construct string for this question being changed.
                    ret.append("'{}' was answered by {}.".format(
                        " → ".join(path + [q.spec['title']]),
                        author,
                    ))
                    continue

                # Scan sub-tasks for new answers.
                for subtask in a.answered_by_task.all():
                    ret.extend(summarize_task_changes(subtask, path+[subtask.title], seen_tasks))

            # If there are a lot of changes, summarize.
            if len(ret) >= 5 and all_authors:
                return ["{} questions in {} were answered by {}.".format(
                    len(ret),
                    " → ".join(path) or "this task",
                    ", ".join(all_authors),
                )]

            return ret


        ret["changes"] = " ".join(summarize_task_changes(task, [], set()))

    return JsonResponse(ret)

@login_required
def start_a_discussion(request):
    # This view function creates a discussion, or returns an existing one.

    # Validate and retreive the Task and ModuleQuestion that the discussion
    # is to be attached to.
    task = get_object_or_404(Task, id=request.POST['task'])
    q = get_object_or_404(ModuleQuestion, id=request.POST['question'])

    # The user may not have permission to create - only to get.

    tq_filter = { "task": task, "question": q }
    tq = TaskAnswer.objects.filter(**tq_filter).first()
    if not tq:
        # Validate user can create discussion. Any user who can read the task can start
        # a discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the TaskAnswer for this task. It may not exist yet.
        tq, isnew = TaskAnswer.objects.get_or_create(**tq_filter)

    discussion = Discussion.get_for(task.project.organization, tq)
    if not discussion:
        # Validate user can create discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the Discussion.
        discussion = Discussion.get_for(task.project.organization, tq, create=True)

    return JsonResponse(discussion.render_context_dict(request.user))

@login_required
def analytics(request):
    from django.db.models import Avg, Count

    from guidedmodules.models import ModuleQuestion

    if not request.user.is_staff:
        return HttpResponseForbidden()

    def compute_table(opt):
        qs = InstrumentationEvent.objects\
            .filter(event_type=opt["event_type"])\
            .values(opt["field"])

        overall = qs.aggregate(
                avg_value=Avg('event_value'),
                count=Count('event_value'),
            )
        
        rows = qs\
            .exclude(**{opt["field"]: None})\
            .annotate(
                avg_value=Avg('event_value'),
                count=Count('event_value'),
            )\
            .exclude(avg_value=None)\
            .order_by('-avg_value')\
            [0:10]

        bulk_objs = opt['model'].objects.in_bulk(r[opt['field']] for r in rows)

        opt.update({
            "overall": round(overall['avg_value']) if overall['avg_value'] is not None else "No Data",
            "n": overall['count'],
            "rows": [{
                    "obj": str(bulk_objs[v[opt['field']]]),
                    "label": opt['label']( bulk_objs[v[opt['field']]] ),
                    "detail": opt['detail']( bulk_objs[v[opt['field']]] ),
                    "n": v['count'],
                    "value": round(v['avg_value']),
                }
                for v in rows ],
        })
        return opt

    return render(request, "analytics.html", {
        "tables": [
            compute_table({
                "event_type": "task-done",
                "title": "Hardest Modules",

                "model": Module,
                "field": "module",

                "quantity": "Time To Finish (sec)",
                "label": lambda m : m.title,
                "detail": lambda m : "version id %d" % m.id,
            }),

            compute_table({
                "event_type": "task-question-answer",
                "title": "Hardest Questions",

                "model": ModuleQuestion,
                "field": "question",

                "quantity": "Time To Answer (sec)",
                "label": lambda q : q.spec['title'],
                "detail": lambda q : "%s, version id %d" % (q.module.title, q.module.id),
            }),

            compute_table({
                "event_type": "task-question-interact-first",
                "title": "Longest Time to First Interaction",

                "model": ModuleQuestion,
                "field": "question",

                "quantity": "Time To First Interaction (sec)",
                "label": lambda q : q.spec['title'],
                "detail": lambda q : "%s, version id %d" % (q.module.title, q.module.id),
            }),

            compute_table({
                "event_type": "task-question-request-duration",
                "title": "Slowest Loading Modules",

                "model": Module,
                "field": "module",

                "quantity": "HTTP Request Duration (ms)",
                "label": lambda m : m.spec['title'],
                "detail": lambda m : "version id %d" % m.id,
            }),

        ]
    })
