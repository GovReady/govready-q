from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import Module, Task, TaskAnswer, TaskAnswerHistory
import guidedmodules.module_logic as module_logic
from discussion.models import Discussion
from siteapp.models import User, Invitation, Project, ProjectMembership

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
    return HttpResponseRedirect(task.get_absolute_url())

@login_required
def next_question(request, taskid, taskslug):
    # Get the Task.
    task = get_object_or_404(Task, id=taskid)

    # Load the answers the user has saved so far.
    answered = task.get_answers()

    # Process form data.
    if request.method == "POST":
        # does user have write privs?
        if not task.has_write_priv(request.user):
            return HttpResponseForbidden()

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
            # parse
            if q.spec["type"] == "multiple-choice":
                # multiple items submitted
                value = request.POST.getlist("value")
            else:
                # single item submitted
                value = request.POST.get("value", "").strip()

            # validate
            try:
                value = module_logic.validator.validate(q, value)
            except ValueError as e:
                # client side validation should have picked this up
                return JsonResponse({ "status": "error", "message": str(e) })

            cleared = False
        else:
            raise ValueError("invalid 'method' parameter %s" + request.POST.get("method", "<not set>"))

        # save answer - get the TaskAnswer instance first
        question, isnew = TaskAnswer.objects.get_or_create(
            task=task,
            question=q,
        )

        # normal redirect - reload the page
        redirect_to = request.path

        # fetch the task that answers this question
        answered_by_tasks = []
        if q.spec["type"] in ("module", "module-set") and not cleared:
            # get the module that the tasks for this question must use
            m1 = Module.objects.get(id=q.spec["module-id"])

            if value == "__new":
                # Create a new task, and we'll redirect to it immediately.
                t = Task.objects.create(
                    editor=request.user,
                    project=task.project,
                    module=m1,
                    title=m1.title)

                answered_by_tasks = [t]
                redirect_to = t.get_absolute_url()

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
                    if t.module != m1 or not t.has_read_priv(request.user):
                        raise ValueError("invalid task ID")
                if q.spec["type"] == "module" and len(answered_by_tasks) != 1:
                    raise ValueError("did not provide exactly one task ID")
            
            value = None

        # Create a new TaskAnswerHistory if the answer is actually changing.
        current_answer = question.get_current_answer()
        if not current_answer and cleared:
            # user is trying to clear but there is no answer yet, so do nothing
            pass

        elif not current_answer \
            or value != current_answer.value \
            or set(answered_by_tasks) != set(current_answer.answered_by_task.all()) \
            or cleared != current_answer.cleared:

            answer = TaskAnswerHistory.objects.create(
                taskanswer=question,
                answered_by=request.user,
                value=value,
                cleared=cleared)
            for t in answered_by_tasks:
                answer.answered_by_task.add(t)

            # kick the Task and TaskAnswer's updated field
            task.save(update_fields=[])
            question.save(update_fields=[])

        # return to a GET request
        return JsonResponse({ "status": "ok", "redirect": redirect_to })

    # Ok this is a GET request....

    # What question are we displaying?
    if "q" in request.GET:
        q = task.module.questions.get(key=request.GET["q"])
    else:
        # Display next unanswered question.
        q = module_logic.next_question(answered)

    if q:
        # Is there a TaskAnswer for this yet?
        taskq = TaskAnswer.objects.filter(task=task, question_id=q.id).first()
    else:
        # We're going to show the finished page - there is no question.
        taskq = None

    # Does the user have read privs here?
    def read_priv():
        if task.has_read_priv(request.user, allow_access_to_deleted=True):
            # See below for checking if the task was deleted.
            return True
        if not taskq:
            return False
        d = Discussion.get_for(taskq)
        if not d:
            return False
        if d.is_participant(request.user):
            return True
        return False
    if not read_priv():
        return HttpResponseForbidden()

    # We skiped the check for whether the Task is deleted above. Now
    # check for that.
    if task.deleted_at:
        # The Task is deleted. If the user would have had access to it,
        # show a more friendly page than an access denied. Discussion
        # guests will have been denied above because is_participant
        # will fail on deleted tasks.
        return HttpResponse("This module was deleted by its editor or a project administrator.")

    # Redirect if slug is not canonical. We do this after checking for
    # read privs so that we don't reveal the task's slug to unpriv'd users.
    if request.path != task.get_absolute_url():
        return HttpResponseRedirect(task.get_absolute_url())

    # Display requested question.

    # Common context variables.
    import json
    context = {
        "m": task.module,
        "task": task,
        "is_discussion_guest": not task.has_read_priv(request.user), # i.e. only here for discussion
        "write_priv": task.has_write_priv(request.user),
        "send_invitation": json.dumps(Invitation.form_context_dict(request.user, task.project, [task.editor])),
        "open_invitations": task.get_open_invitations(request.user),
        "source_invitation": task.invitation_history.filter(accepted_user=request.user).order_by('-created').first(),
    }

    if not q:
        # There is no next question - the module is complete.
        context.update({
            "output": task.render_output_documents(answered),
            "all_questions": [
                {
                    "question": q,
                    "skipped": q.spec.get("required") and (answered.answers.get(q.key) is None),
                }
                for q in task.module.questions.all().order_by('definition_order')
                if module_logic.impute_answer(q, answered) is None ],
        })
        return render(request, "module-finished.html", context)

    else:
        answer = None
        if taskq:
            answer = taskq.get_current_answer()
            if answer and answer.cleared:
                # If the answer is cleared, treat as if it had not been answered.
                answer = None

        # for "module"-type questions
        # what Module answers this question?
        answer_module = Module.objects.get(id=q.spec["module-id"]) if q.spec["type"] in ("module", "module-set") else None
        # what existing Tasks are of that type?
        answer_tasks = [t for t in Task.objects.filter(project=task.project, module=answer_module)
            if t.has_read_priv(request.user)]
        for t in answer_tasks:
            t.can_write = t.has_write_priv(request.user)

        context.update({
            "DEBUG": settings.DEBUG,
            "q": q,
            "prompt": task.render_question_prompt(q),
            "history": taskq.get_history() if taskq else None,
            "answer": answer,
            "discussion": Discussion.get_for(taskq) if taskq else None,

            "answer_module": answer_module,
            "answer_tasks": answer_tasks,
            "answer_tasks_show_user": len([ t for t in answer_tasks if t.editor != request.user ]) > 0,
        })
        return render(request, "question.html", context)

@login_required
def change_task_state(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    task = get_object_or_404(Task, id=request.POST["id"])
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
