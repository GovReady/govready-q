from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from questions import Module
from .models import Project, ProjectMembership, Task, TaskQuestion, TaskAnswer
from discussion.models import Discussion
from siteapp.models import User, Invitation

@login_required
def new_project(request):
    from django.forms import ModelForm

    class NewProjectForm(ModelForm):
        class Meta:
            model = Project
            fields = ['title', 'notes']
            help_texts = {
                'title': 'Give your project a descriptive name.',
                'notes': 'Optionally write some notes. If you invite other users to your project team, they\'ll be able to see this too.',
            }

    form = NewProjectForm()
    if request.method == "POST":
        # Save and then go back to the home page to see it.
        form = NewProjectForm(request.POST)
        if not form.errors:
            with transaction.atomic():
                project = form.save()
                ProjectMembership.objects.create(
                    project=project,
                    user=request.user,
                    is_admin=True)
            return HttpResponseRedirect("/")

    return render(request, "new-project.html", {
        "first": not ProjectMembership.objects.filter(user=request.user).exists(),
        "form": form,
    })

def x():
    p = Project.objects.create(
        title="New Project",
        notes="Description of your new project.")
    ProjectMembership.objects.create(project=p, user=request.user, is_admin=True)
    return HttpResponseRedirect(p.get_absolute_url())

@login_required
def new_task(request):
    # Create a new task.

    # Validate that the module ID is valid.
    m = Module.load(request.GET['module'])

    # Validate that the user is permitted to create a task within the indicated Project.
    project = get_object_or_404(Project, id=request.GET["project"], members__user=request.user)

    # Create and redirect to start it.
    task = Task.objects.create(
        editor=request.user,
        project=project,
        module_id=m.id,
        title=m.title)
    return HttpResponseRedirect(task.get_absolute_url() + "/start")

@login_required
def next_question(request, taskid, taskslug, intropage=None):
    # Get the Task.
    task = get_object_or_404(Task, id=taskid)

    # Load the questions module.
    m = task.load_module()

    # Load the answers the user has saved so far.
    answered = task.get_answers()

    # Process form data.
    if request.method == "POST":
        if intropage:
            return HttpResponseForbidden()

        # does user have write privs?
        if not task.has_write_priv(request.user):
            return HttpResponseForbidden()

        # validate question
        q = request.POST.get("question")
        if q not in m.questions_by_id:
            return HttpResponse("invalid question id", status=400)
        q = m.questions_by_id[q]

        # validate and parse value
        if request.POST.get("method") == "clear":
            value = None
        else:
            # parse
            if q.type == "multiple-choice":
                # multiple items submitted
                value = request.POST.getlist("value")
            else:
                # single item submitted
                value = request.POST.get("value", "").strip()

            # validate
            try:
                value = q.validate(value)
            except ValueError as e:
                # client side validation should have picked this up
                return HttpResponse("invalid value: " + str(e), status=400)

        # save answer - get the TaskQuestion instance first
        question, isnew = TaskQuestion.objects.get_or_create(
            task=task,
            question_id=q.id,
        )

        # normal redirect - reload the page
        redirect_to = request.path

        # fetch the task that answers this question
        answered_by_task = None
        if q.type == "module":
            if value == None:
                # answer is being cleared
                t = None
            elif value == "__new":
                # Create a new task, and we'll redirect to it immediately.
                m1 = Module.load(q.module_id) # validate input
                t = Task.objects.create(
                    editor=request.user,
                    project=task.project,
                    module_id=m1.id,
                    title=m1.title)

                redirect_to = t.get_absolute_url() + "/start"

            else:
                # user selects an existing Task (TODO :ensure the user has access to it)
                t = Task.objects.get(project=task.project, id=int(value))

            answered_by_task = t
            value = None

        # Create a new TaskAnswer if the answer is actually changing.
        current_answer = question.get_answer()
        if not current_answer or (value != current_answer.value or answered_by_task != current_answer.answered_by_task):
            answer = TaskAnswer.objects.create(
                question=question,
                answered_by=request.user,
                value=value,
                answered_by_task=answered_by_task,
            )

            # kick the task and questions's updated field
            task.save(update_fields=[])
            question.save(update_fields=[])

        # return to a GET request
        return HttpResponseRedirect(redirect_to)

    # Ok this is a GET request....

    # What question are we displaying?
    q = request.GET.get("q")
    if q:
        if q not in m.questions_by_id:
            raise Http404()
        q = m.questions_by_id[q]
    else:
        # Display next unanswered question.
        q = m.next_question(answered)

    if q:
        # Is there a TaskQuestion for this yet?
        taskq = TaskQuestion.objects.filter(task=task, question_id=q.id).first()
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
    if request.path != task.get_absolute_url() + (intropage or ""):
        return HttpResponseRedirect(task.get_absolute_url())

    # Display requested question.

    # Common context variables.
    import json
    context = {
        "task": task,
        "write_priv": task.has_write_priv(request.user),
        "send_invitation": json.dumps(Invitation.form_context_dict(request.user, task.project)) if task.project else None,
    }

    if intropage:
        context.update({
            "introduction": m.render_introduction(),
        })
        return render(request, "module-intro.html", context)

    elif not q:
        # There is no next question - the module is complete.
        context.update({
            "m": m,
            "output": task.get_output(answered),
            "all_questions": filter(lambda q : not q.impute_answer(answered), m.questions),
        })
        return render(request, "module-finished.html", context)

    else:
        answer = None
        if taskq:
            answer = taskq.get_answer()

        context.update({
            "DEBUG": settings.DEBUG,
            "module": m,
            "q": q,
            "prompt": q.render_prompt(task.get_answers()),
            "history": taskq.get_history() if taskq else None,
            "answer": answer,
            "discussion": Discussion.get_for(taskq) if taskq else None,

            "answer_module": Module.load(q.module_id) if q.module_id else None,
            "answer_tasks": Task.objects.filter(project=task.project, module_id=q.module_id),
            "answer_tasks_show_user": Task.objects.filter(project=task.project).exclude(editor=request.user).exists(),
            "answer_answered_by_task_can_write": answer.answered_by_task.has_write_priv(request.user) if answer and answer.answered_by_task else None,
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
