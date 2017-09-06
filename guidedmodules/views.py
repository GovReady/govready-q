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

@login_required
def new_task(request):
    # Create a new task by answering a module question of a project rook task.
    project = get_object_or_404(Project, id=request.POST["project"], organization=request.organization)

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
    task = get_object_or_404(Task, id=taskid, project__organization=request.organization)
    if not task.has_read_priv(request.user): raise Http404()

    # Check that the Task's Module has assets and that this path is
    # one of them.
    if not task.module.assets or asset_path not in task.module.assets.paths:
        raise Http404()

    # Look up the ModuleAsset object.
    content_hash = task.module.assets.paths[asset_path]
    asset = task.module.assets.assets.get(content_hash=content_hash)

    # Get the dbstorage.models.StoredFile instance which holds
    # an auto-detected mime type.
    from dbstorage.models import StoredFile
    sf = StoredFile.objects.only("mime_type").get(path=asset.file.name)

    # Construct the response. The file content is probably untrusted, in which
    # case it must not be served as an inline resource from our domain unless it is
    # an image, which browsers won't execute.
    if (sf.mime_type and sf.mime_type.startswith("image/")) or task.module.assets.trust_assets:
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
    def inner_func(request, taskid, taskslug, pagepath, question_key, *args):
        # Get the Task.
        task = get_object_or_404(Task, id=taskid, project__organization=request.organization)

        # If this task is actually a project root, redirect away from here.
        if task.root_of.first() is not None:
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
                d = Discussion.get_for(request.organization, taskans)
                if d and d.is_participant(request.user):
                    return True
            return False
        if not read_priv():
            return HttpResponseForbidden()

        # We skiped the check for whether the Task is deleted above. Now
        # check for that and provide a more specific error.
        if task.deleted_at:
            # The Task is deleted. If the user would have had access to it,
            # show a more friendly page than an access denied. Discussion
            # guests will have been denied above because is_participant
            # will fail on deleted tasks.
            return HttpResponse("This module was deleted by its editor or a project administrator.")

        # Redirect if slug is not canonical. We do this after checking for
        # read privs so that we don't reveal the task's slug to unpriv'd users.
        # Only issue a redirect on GET requests. Since a POST might be saving
        # data, it's fine if the path isn't canonical and we want to allow the
        # save to complete. Also skip if the extra positional args 'args' has
        # any values, which means we're on some subpage that we don't know
        # how to re-form the URL for at the moment.
        if request.method == "GET" and taskslug != task.get_slug() and len(args) == 0:
            return HttpResponseRedirect(task.get_absolute_url() + pagepath + question_key)

        # Prepare for reading/writing ephemeral encryption.
        from datetime import timedelta
        ephemeral_encryption_lifetime = timedelta(hours=3).total_seconds()
        ephemeral_encryption_lifetime_nice = "3 hours"
        ephemeral_encryption_cookies = []
        class EncryptionProvider():
            key_id_pattern = "encr_eph_%d"
            def set_new_ephemeral_user_key(self, key):
                # Find a new ID for this key.
                key_id_pattern = EncryptionProvider.key_id_pattern
                key_id = 1
                while (key_id_pattern % key_id) in request.COOKIES: key_id += 1
                # We can't set a cookie here because we don't have an HttpResponse
                # object yet. So just record the cookie for now and set it later.
                ephemeral_encryption_cookies.append((
                    key_id_pattern % key_id,
                    key))
                # Return the key's ID and its lifetime.
                return key_id, ephemeral_encryption_lifetime
            def get_ephemeral_user_key(self, key_id):
                return request.COOKIES.get(EncryptionProvider.key_id_pattern % key_id)
        def set_ephemeral_encryption_cookies(response):
            # No need to sign the cookies since if it's tampered
            # with, the user simply won't be able to decrypt things.
            for key, value in ephemeral_encryption_cookies:
                response.set_cookie(key, value=value,
                    max_age=ephemeral_encryption_lifetime,
                    httponly=True)

        # Load the answers the user has saved so far, and fetch imputed
        # answers and next-question info.
        answered = task.get_answers(decryption_provider=EncryptionProvider())\
            .with_extended_info()

        # Common context variables.
        context = {
            "DEBUG": settings.DEBUG,
            "ADMIN_ROOT_URL": settings.SITE_ROOT_URL + "/admin",

            "m": task.module,
            "task": task,
            "is_discussion_guest": not task.has_read_priv(request.user), # i.e. only here for discussion
            "write_priv": task.has_write_priv(request.user),
            "send_invitation": Invitation.form_context_dict(request.user, task.project, [task.editor]),
            "open_invitations": task.get_open_invitations(request.user, request.organization),
            "source_invitation": task.get_source_invitation(request.user, request.organization),
            "previous_page_type": request.GET.get("previous"),

            "ephemeral_encryption_lifetime": ephemeral_encryption_lifetime_nice,
        }

        # Is this the user's settings page? Hide the blurb to do it.
        if task == request.user.user_settings_task:
           request.suppress_prompt_banner = True

        # Render the view.
        return view_func(request, task, answered, context, question, EncryptionProvider, set_ephemeral_encryption_cookies, *args)

    return inner_func


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
def save_answer(request, task, answered, context, __, EncryptionProvider, set_ephemeral_encryption_cookies):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # does user have write privs?
    if not task.has_write_priv(request.user):
        return HttpResponseForbidden()

    # normal redirect - reload the page
    redirect_to = task.get_absolute_url() + "?previous=nquestion"

    # validate question
    q = task.module.questions.get(id=request.POST.get("question"))

    # validate and parse value
    if request.POST.get("method") == "clear":
        # clear means that the question returns to an unanswered state
        value = None
        cleared = True
    
    elif request.POST.get("method") == "skip":
        # skipped means the question is answered with a null value
        value = None
        cleared = False
    
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

        # run external functions
        if q.spec['type'] == "external-function":
            # Make a deepcopy of some things so that we don't allow the function
            # to mess with our data.
            try:
                value = module_logic.run_external_function(
                    q, answered,
                    project_name=task.project.title,
                    project_url=task.project.organization.get_url(task.project.get_absolute_url())
                )
            except ValueError as e:
                return JsonResponse({ "status": "error", "message": str(e) })

        cleared = False

    elif request.POST.get("method") == "review":
        # Update the reviewed flag on the answer.
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
                module=q.answer_type_module,
                title=q.answer_type_module.title)

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
        if question.save_answer(value, answered_by_tasks, answered_by_file, request.user, "web", encryption_provider=EncryptionProvider()):
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

    # Apply any new ephemeral encryption cookies now that we have
    # an HttpResponse object.
    set_ephemeral_encryption_cookies(response)

    # Return the response.
    return response


@task_view
def show_question(request, task, answered, context, q, EncryptionProvider, set_ephemeral_encryption_cookies):
    # Always hide the fill-out-your-profile blurb on all question pages - it's
    # distracting from answering the question at hand. See task_view.
    request.suppress_prompt_banner = True

    # If this question cannot currently be answered (i.e. dependencies are unmet),
    # then redirect away from this page. If the user is allowed to use the authoring
    # tool, then allow seeing this question so they can edit all questions.
    authoring_tool_enabled = task.module.is_authoring_tool_enabled(request.user)
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
        answer_tasks = Task.get_all_tasks_readable_by(request.user, request.organization)\
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
    def render_markdown_field(field, output_format, **kwargs):
        template = q.spec.get(field)
        if not template:
            return None
        if not isinstance(template, str):
            raise ValueError("%s question %s %s is not a string" % (repr(q.module), q.key, field))
        return module_logic.render_content({
                "template": template,
                "format": "markdown",
            },
            answered,
            output_format,
            "%s question %s %s" % (repr(q.module), q.key, field),
            **kwargs
        )

    # Get any existing answer for this question.
    existing_answer = None
    if answer:
        existing_answer = answer.get_value(decryption_provider=EncryptionProvider())

        # For longtext questions, because the WYSIWYG editor is initialized with HTML,
        # render the value as HTML.
        if existing_answer and q.spec["type"] == "longtext":
            import CommonMark
            existing_answer = CommonMark.HtmlRenderer().render(CommonMark.Parser().parse(existing_answer))

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

    context.update({
        "header_col_active": "start" if (len(answered.as_dict()) == 0 and q.spec["type"] == "interstitial") else "questions",
        "q": q,
        "title": title,
        "prompt": prompt,
        "placeholder_answer": render_markdown_field("placeholder", "text") or "", # Render Jinja2 template but don't turn Markdown into HTML.
        "reference_text": render_markdown_field("reference_text", "html"),
        "history": taskq.get_history() if taskq else None,
        "answer_obj": answer,
        "answer": existing_answer,
        "default_answer": default_answer,
        "review_choices": [(0, 'Not Reviewed'), (1, 'Reviewed'), (2, 'Approved')],
        "discussion": Discussion.get_for(request.organization, taskq) if taskq else None,
        "show_discussion_members_count": True,

        "answer_module": answer_module,
        "answer_tasks": answer_tasks,
        "answer_tasks_show_user": len([ t for t in answer_tasks if t.editor != request.user ]) > 0,

        "context": module_logic.get_question_context(answered, q),

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
        "authoring_tool_enabled": authoring_tool_enabled,
    })
    return render(request, "question.html", context)


@task_view
def task_finished(request, task, answered, context, *unused_args):
    # Either the task is finished, there are required questions that were skipped,
    # or the user is returning to the finished page directly later and the task
    # might or might not actually be finished.

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

    # Construct the page.
    context.update({
        "had_any_questions": len(set(answered.as_dict()) - answered.was_imputed) > 0,
        "output": task.render_output_documents(answered),
        "context": module_logic.get_question_context(answered, None),
        "authoring_tool_enabled": task.module.is_authoring_tool_enabled(request.user),
    })
    return render(request, "module-finished.html", context)


@task_view
def download_answer_file(request, task, answered, context, q, EncryptionProvider, set_ephemeral_encryption_cookies, history_id):
    # Get the TaskAnswerHistory object referenced in the URL.
    tah = get_object_or_404(TaskAnswerHistory, id=history_id, taskanswer__task=task, taskanswer__question=q)

    # It should have a file question and a file answer.
    if q.spec["type"] != "file": raise Http404()
    if not tah.answered_by_file.name: raise Http404()

    # Get the dbstorage.models.StoredFile instance which holds
    # an auto-detected mime type.
    from dbstorage.models import StoredFile
    sf = StoredFile.objects.only("mime_type").get(path=tah.answered_by_file.name)

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
    resp = HttpResponse(tah.answered_by_file, content_type=mime_type)
    resp['Content-Disposition'] = disposition + '; filename=' + os.path.basename(tah.answered_by_file.name)


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


@login_required
def instrumentation_record_interaction(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # Get event variables.
    
    task = get_object_or_404(Task, id=request.POST["task"], project__organization=request.organization)
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

        task = get_object_or_404(Task, id=request.POST["task"], project__organization=request.organization)
        if not task.has_write_priv(request.user):
            return HttpResponseForbidden()
        if not task.module.is_authoring_tool_enabled(request.user):
            return HttpResponseForbidden()

        # Run inner function.
        return f(request, task)

    return g

@authoring_tool_auth
def authoring_new_question(request, task):
    # Find a new unused question identifier.
    ids_in_use = set(task.module.questions.values_list("key", flat=True))
    key = 0
    while "q" + str(key) in ids_in_use: key += 1
    key = "q" + str(key)

    # Get the highest definition_order in use so far.
    definition_order = max([0] + list(task.module.questions.values_list("definition_order", flat=True))) + 1

    # Make a new question instance.
    question = ModuleQuestion(
        module=task.module,
        key=key,
        definition_order=definition_order,
        spec={
            "type": "text",
            "title": "New Question Title",
            "prompt": "Enter some text.",
        }
        )
    question.save()

    # Write to disk if possible.
    try:
        question.module.serialize_to_disk()
    except:
        pass

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
                else:
                    spec[field] = value

        # For module-type questions the "module-id" form field gives a Module instance
        # ID, which we need to set in the Question.answer_type_module field as well
        # as in the Question.spec["module-id"] field for validation and serialization
        # to YAML on disk.
        question.answer_type_module = None
        if request.POST.get("module-id") and spec["type"] in ("module", "module-set"):
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
        validate_question(question.module.spec, spec)

    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })

    # Save.
    question.spec = spec
    question.save()

    # Write to disk if possible.
    try:
        question.module.serialize_to_disk()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not update local YAML file: " + str(e) })

    # Return status. The browser will reload/redirect --- if the question key
    # changed, this sends the new key.
    return JsonResponse({ "status": "ok", "redirect": task.get_absolute_url_to_question(question) })


@login_required
def change_task_state(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    task = get_object_or_404(Task, id=request.POST["id"], project__organization=request.organization)
    if not task.has_write_priv(request.user, allow_access_to_deleted=True):
        return HttpResponseForbidden()

    if request.POST['state'] == "delete":
        task.deleted_at = timezone.now()
    elif request.POST['state'] == "undelete":
        task.deleted_at = None
    else:
        return HttpResponseForbidden()

    task.save(update_fields=["deleted_at"])

    return HttpResponse("ok")

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

    discussion = Discussion.get_for(request.organization, tq)
    if not discussion:
        # Validate user can create discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the Discussion.
        discussion = Discussion.get_for(request.organization, tq, create=True)

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

        # When we look at the analytics page in an organization domain,
        # we only pull instrumentation for projects within that organization.
        if hasattr(request, "organization"):
            qs = qs.filter(project__organization=request.organization)

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
        "base_template": "base.html" if hasattr(request, "organization") else "base-landing.html",
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
