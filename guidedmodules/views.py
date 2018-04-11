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
            "send_invitation": Invitation.form_context_dict(request.user, task.project, [task.editor]),
            "open_invitations": task.get_open_invitations(request.user, request.organization),
            "source_invitation": task.get_source_invitation(request.user, request.organization),
            "previous_page_type": request.GET.get("previous"),
        }

        # Render the view.
        return view_func(request, task, answered, context, question, *args)

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
def save_answer(request, task, answered, context, __):
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
        answer_tasks = Task.get_all_tasks_readable_by(request.user, request.organization, recursive=True)\
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
            import CommonMark
            existing_answer = CommonMark.HtmlRenderer().render(CommonMark.Parser().parse(existing_answer))

    # For file-type questions that have been answered, render the existing
    # answer so that we don't need redundant logic for showing a thumbnail
    # and providing a download link.
    answer_rendered = None
    if taskq and taskq.question.spec["type"] == "file" and answer:
        from .module_logic import TemplateContext, RenderedAnswer, HtmlAnswerRenderer
        tc = TemplateContext(answered, HtmlAnswerRenderer(show_metadata=False))
        ra = RenderedAnswer(task, taskq.question, answer, existing_answer, tc)
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
        "can_review": task.has_review_priv(request.user),
        "review_choices": TaskAnswerHistory.REVIEW_CHOICES,
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
        "authoring_tool_enabled": task.module.is_authoring_tool_enabled(request.user),
    })
    return render(request, "module-finished.html", context)


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

    # Find the document with the named id.
    for doc in task.render_output_documents(answered, use_data_urls=True):
        if doc.get("id") == document_id:
            break
    else:
        raise Http404()

    pandoc_opts = {
        "plain": ("plain", "txt", "text/plain"),
        "markdown": ("markdown_github", "md", "text/plain"),
        "docx": ("docx", "docx", "application/octet-stream"),
        "odt": ("odt", "odt", "application/octet-stream"),
    }

    if download_format == "markdown" and doc["format"] == "markdown":
        # When a Markdown output is requested for a template that is
        # authored in markdown, use its markdown output format. Otherwise
        # use pandoc below.
        return HttpResponse(doc["markdown"], content_type="text/plain")

    elif download_format == "html":
        # Return the raw HTML.
        return HttpResponse(doc["html"], content_type="text/html")

    elif download_format == "pdf":
        # Convert the HTML to a PDF using wkhtmltopdf.
        
        # Mark the encoding explicitly, to match the html.encode() argument below.
        html = doc["html"]
        html = '<meta charset="UTF-8" />' + html

        import subprocess # nosec
        cmd = ["/usr/bin/xvfb-run", "--", "/usr/bin/wkhtmltopdf",
               "-q", # else errors go to stdout
               "--disable-javascript",
               "--encoding", "UTF-8",
               "-s", "Letter", # page size
               "-", "-"]
        with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
            stdout, stderr = proc.communicate(
                  html.encode("utf8"),
                  timeout=10)
            if proc.returncode != 0: raise subprocess.CalledProcessError(proc.returncode, ' '.join(cmd))

        resp = HttpResponse(stdout, "application/pdf")
        resp['Content-Disposition'] = 'inline; filename=' + document_id + ".pdf"
        return resp

    elif download_format in pandoc_opts:
        # These are pandoc output formats. 
        # odt and some other formats cannot pipe to stdout, so we always
        # generate a temporary file.
        pandoc_format, file_extension, mime_type = pandoc_opts[download_format]
        import tempfile, os.path, subprocess # nosec
        with tempfile.TemporaryDirectory() as tempdir:
            # convert from HTML to something else, writing to a temporary file
            outfn = os.path.join(tempdir, document_id + "." + file_extension)
            with subprocess.Popen(
                ["/usr/bin/pandoc", "-f", "html", "-t", pandoc_format, "-o", outfn],
                stdin=subprocess.PIPE
                ) as proc:
                proc.communicate(
                    doc["html"].encode("utf8"),
                    timeout=10)
                if proc.returncode != 0: raise subprocess.CalledProcessError(0, '')

            # send the temporary file to the response
            with open(outfn, "rb") as f:
                resp = HttpResponse(f.read(), mime_type)
                resp['Content-Disposition'] = 'inline; filename=' + document_id + "." + file_extension
                return resp

    return HttpResponse("Invalid download format.")


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
@transaction.atomic
def authoring_edit_reload_app(request, task):
    # Refresh the app that this Task is a part of by reloading all of the
    # Modules associated with this instance of the app.
    from .module_sources import AppImportUpdateMode, ValidationError, IncompatibleUpdate
    from .module_sources import ModuleDefinitionError
    with task.module.source.open() as store:
        for app in store.list_apps():
            # Only update using the app that provided this Task's Module.
            if app.name != task.module.app.appname:
                continue

            # Import.
            try:
                app.import_into_database(
                    AppImportUpdateMode.ForceUpdate
                     if request.POST.get("force") == "true"
                     else AppImportUpdateMode.CompatibleUpdate,
                    task.module.app)
            except (ModuleDefinitionError, ValidationError, IncompatibleUpdate) as e:
                return JsonResponse({ "status": "error", "message": str(e) })

    return JsonResponse({ "status": "ok" })

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
    if task.module.spec.get("type") != "project":
        spec = {
            "id": key,
            "type": "text",
            "title": "New Question Title",
            "prompt": "Enter some text.",
        }
    else:
        spec = {
            "id": key,
            "type": "module",
            "title": "New Question Title",
            "protocol": "choose-a-module-or-enter-a-protocol-id",
        }

    # Make a new question instance.
    question = ModuleQuestion(
        module=task.module,
        key=key,
        definition_order=definition_order,
        spec=spec
        )
    question.save()

    # Write to disk. Errors writing should not be suppressed because
    # saving to disk is a part of the contract of how app editing works.
    try:
        question.module.serialize_to_disk()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not update local YAML file: " + str(e) })

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
        spec = validate_module(spec, is_authoring_tool=True)
    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })

    # Save.
    task.module.spec = spec
    task.module.save()

    # Write to disk. Errors writing should not be suppressed because
    # saving to disk is a part of the contract of how app editing works.
    try:
        task.module.serialize_to_disk()
    except Exception as e:
        return JsonResponse({ "status": "error", "message": "Could not update local YAML file: " + str(e) })

    # Return status. The browser will reload/redirect --- if the question key
    # changed, this sends the new key.
    return JsonResponse({ "status": "ok", "redirect": task.get_absolute_url() })


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
def get_task_timetamp(request):
    # Get the 'updated' timestamp on the task and if 'get_changes_since'
    # is passed, scan for new answers within this project and return a
    # summary of the changes.

    # Check access.
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    task = get_object_or_404(Task, id=request.POST["id"], project__organization=request.organization)
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
