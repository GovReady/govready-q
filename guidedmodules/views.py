from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from questions import Module
from .models import Project, ProjectMembership, Task, TaskQuestion, TaskAnswer, Invitation, Discussion, Comment
from siteapp.models import User

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

    # Does user have read privs?
    if not task.has_read_priv(request.user):
        return HttpResponseForbidden()

    # Does user have write privs? The user is either the editor or an admin of
    # the project that the task belongs too.
    write_priv = task.has_write_priv(request.user)

    # Redirect if slug is not canonical.
    if request.path != task.get_absolute_url() + (intropage or ""):
        return HttpResponseRedirect(task.get_absolute_url())

    # Load the questions module.
    m = task.load_module()

    # Load the answers the user has saved so far.
    answered = task.get_answers_dict()

    # Process form data.
    if request.method == "POST":
        if intropage:
            return HttpResponseForbidden()

        # does user have write privs?
        if not write_priv:
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

                redirect_to = t.get_absolute_url()

                from django.contrib import messages
                messages.add_message(request, messages.INFO, 'You are now editing a new module to answer the previous question.')

            else:
                # user selects an existing Task (TODO :ensure the user has access to it)
                t = Task.objects.get(project=task.project, id=int(value))

            answered_by_task = t
            value = (t.get_answers_dict() if t else None)

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


    # Display requested question.
    if "q" in request.GET:
        try:
            q = m.questions_by_id[request.GET['q']]
        except KeyError:
            raise Http404()

    else:
        # Display next unanswered question.
        q = m.next_question(answered)

    # Common context variables.
    import json
    context = {
        "task": task,
        "write_priv": write_priv,
        "active_invitation_to_transfer_editorship": task.get_active_invitation_to_transfer_editorship(request.user),
        "source_invitation": task.get_source_invitation(request.user),

        "send_invitation": json.dumps(Invitation.form_context_dict(request.user, task.project)) if task.project else None,
    }

    if intropage:
        context.update({
            "introduction": m.render_introduction(),
        })
        return render(request, "module-intro.html", context)

    elif not q:
        # There is no next question - the module is complete.

        # Set imputed answers
        m.add_imputed_answers(answered)
        def module_loader(task):
            return (task.load_module(), task.get_answers_dict())
        m.prerender_answers(answered, module_loader)

        # Render.
        context.update({
            "m": m,
            "output": m.render_output(answered),
            "all_questions": filter(lambda q : not q.impute_answer(answered), m.questions),
            "is_answer_to": task.is_answer_to.filter(answered_by=request.user).order_by('-updated').first(),
        })
        return render(request, "module-finished.html", context)
    else:
        taskq = TaskQuestion.objects.filter(task=task, question_id=q.id).first()
        answer = None
        if taskq:
            answer = taskq.get_answer()

        context.update({
            "DEBUG": settings.DEBUG,
            "module": m,
            "q": q,
            "prompt": q.render_prompt(task.get_answers_dict()),
            "history": taskq.get_history() if taskq else None,
            "answer": answer,
            "discussion": Discussion.objects.filter(for_question=taskq).first(),

            "answer_module": Module.load(q.module_id) if q.module_id else None,
            "answer_tasks": Task.objects.filter(project=task.project, module_id=q.module_id),
            "answer_tasks_show_user": Task.objects.filter(project=task.project).exclude(editor=request.user).exists(),
            "answer_task": Task.objects.filter(is_answer_to__question__question_id=q.id),
        })
        return render(request, "question.html", context)

@login_required
def send_invitation(request):
    import email_validator
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    try:
        if not request.POST['user_id'] and not request.POST['user_email']:
            raise ValueError("Select a team member or enter an email address.")

        # if a discussion is given, validate that the requesting user is a participant
        # able to invite guests
        into_discussion = None
        if "into_discussion" in request.POST:
            into_discussion = get_object_or_404(Discussion, id=request.POST["into_discussion"])
            if not into_discussion.can_invite_guests(request.user):
                return HttpResponseForbidden()

        inv = Invitation.objects.create(
            # who is sending the invitation?
            from_user=request.user,
            from_project=Project.objects.filter(id=request.POST["project"], members__user=request.user).first(), # validate that the user is a team member
            
            # what prompted this invitation?
            prompt_task=Task.objects.get(id=request.POST["prompt_task"], editor=request.user) if request.POST.get("prompt_task") else None,
            prompt_question_id=request.POST.get("prompt_question_id"),

            # what is the recipient being invited to? validate that the user is an admin of this project
            # or an editor of the task being reassigned.
            into_project=(request.POST.get("add_to_team", "") != "") and Project.objects.filter(id=request.POST["project"], members__user=request.user, members__is_admin=True).exists(),
            into_new_task_module_id=request.POST.get("into_new_task_module_id"),
            into_task_editorship=Task.objects.get(id=request.POST["into_task_editorship"], editor=request.user) if request.POST.get("into_task_editorship") else None,
            into_discussion=into_discussion,

            # who is the recipient of the invitation?
            to_user=User.objects.get(id=request.POST["user_id"]) if request.POST.get("user_id") else None,
            to_email=request.POST.get("user_email"),

            # personalization
            text = request.POST.get("message", ""),
            email_invitation_code = Invitation.generate_email_invitation_code(),
        )

        inv.send() # TODO: Move this into an asynchronous queue.

        return JsonResponse({ "status": "ok" })

    except ValueError as e:
        return JsonResponse({ "status": "error", "message": str(e) })
    except Exception as e:
        import sys
        sys.stderr.write(str(e) + "\n")
        return JsonResponse({ "status": "error", "message": "There was a problem -- sorry!" })

def accept_invitation(request, code=None):
    assert code.strip() != ""
    inv = get_object_or_404(Invitation, email_invitation_code=code)
    return inv.accept(request)

@login_required
def cancel_invitation(request):
    inv = get_object_or_404(Invitation, id=request.POST['id'], from_user=request.user)
    inv.revoked_at = timezone.now()
    inv.save(update_fields=['revoked_at'])
    return JsonResponse({ "status": "ok" })

@login_required
def start_a_discussion(request):
    # This view function creates a discussion, or returns an existing one.

    # Validate and retreive the Task and question_id that the discussion
    # is to be attached to.
    task = get_object_or_404(Task, id=request.POST['task'])
    m = task.load_module()
    q = m.questions_by_id[request.POST['question']] # validate question ID is ok

    # The user may not have permission to create - only to get.

    tq_filter = { "task": task, "question_id": q.id }
    tq = TaskQuestion.objects.filter(**tq_filter).first()
    if not tq:
        # Validate user can create discussion. Any user who can read the task can start
        # a discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the TaskQuestion for this task. It may not exist yet.
        tq, isnew = TaskQuestion.objects.get_or_create(**tq_filter)

    d_filter = { "project": task.project, "for_question": tq }
    discussion = Discussion.objects.filter(**d_filter).first()
    if not discussion:
        # Validate user can create discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the Discussion.
        discussion = Discussion.objects.get_or_create(**d_filter)[0]

    # Build the event history.
    events = []
    events.extend(tq.get_history())
    events.extend([ comment.render_context_dict() for comment in discussion.comments.all() ])
    events.sort(key = lambda item : item["date_posix"])

    # Get the initial state of the discussion to populate the HTML.
    return JsonResponse({
        "status": "ok",
        "discussion": {
            "id": discussion.id,
            "title": discussion.title,
            "project": {
                "id": discussion.project.id,
                "title": discussion.project.title,
            },
            "can_invite": discussion.can_invite_guests(request.user),
        },
        "guests": [ user.render_context_dict() for user in discussion.external_participants.all() ],
        "events": events,
    })

@login_required
def submit_discussion_comment(request):
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'])

    # Does user have write privs?
    if not ProjectMembership.objects.filter(project=discussion.project, user=request.user).exists() \
        and request.user not in discussion.external_participants.all():
        return JsonResponse({ "status": "error", "message": "No access."})

    # Validate.
    text = request.POST.get("text", "").strip()
    if text == "":
        return JsonResponse({ "status": "error", "message": "No comment entered."})

    # Save comment.
    comment = Comment.objects.create(
        discussion=discussion,
        user=request.user,
        text=text
        )

    # Return the comment for display.
    return JsonResponse(comment.render_context_dict())
