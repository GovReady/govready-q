from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from questions import Module
from .models import Project, ProjectMembership, Task, Answer, Invitation
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
    return HttpResponseRedirect(task.get_absolute_url())

@login_required
def next_question(request, taskid, taskslug):
    # Get the Task.
    task = get_object_or_404(Task, id=taskid)

    # Does user have read privs?
    if task.editor != request.user and not ProjectMembership.objects.filter(project=task.project, user=request.user).exists():
        return HttpResponseNotAllowed(["POST"]) # TODO: use a better status code

    # Redirect if slug is not canonical.
    if request.path != task.get_absolute_url():
        return HttpResponseRedirect(task.get_absolute_url())

    # Load the questions module.
    m = task.load_module()

    # Load the answers the user has saved so far.
    answered = task.get_answers_dict()

    # Process form data.
    if request.method == "POST":
        # does user have write privs?
        if task.editor != request.user:
            return HttpResponseNotAllowed(["POST"])

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

        # save answer
        answer, isnew = Answer.objects.get_or_create(
            task=task,
            question_id=q.id,
            defaults={
                # must specify this to avoid not-null constraint, but we
                # update it again later since it may change if an answer
                # is updated
                "answered_by": request.user
            })

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

        if value != answer.value or answered_by_task != answer.answered_by_task:
            # Move existing answer to history.
            if not isnew:
                answer.history.append({
                    "answered_by": request.user.id,
                    "value": answer.value,
                    "answered_by_task": answer.answered_by_task.id if answer.answered_by_task else None,
                    "notes": answer.notes,
                    "updated": answer.updated,
                })

            # Update Answer.
            answer.answered_by = request.user
            answer.value = value
            answer.answered_by_task = answered_by_task
            answer.save()

            # kick the task's updated field
            task.save(update_fields=[])

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
        "active_invitation_to_transfer_editorship": task.get_active_invitation_to_transfer_editorship(request.user),
        "source_invitation": task.get_source_invitation(request.user),

        "send_invitation": json.dumps(Invitation.form_context_dict(request.user, task.project)) if task.project else None,
    }

    if not q:
        # There is no next question - the module is complete.

        # Set imputed answers
        m.add_imputed_answers(answered)

        # Render.
        context.update({
            "m": m,
            "output": m.render_output(answered),
            "all_questions": filter(lambda q : not q.impute_answer(answered), m.questions),
            "is_answer_of": task.is_answer_of.filter(answered_by=request.user).order_by('-updated').first(),
        })
        return render(request, "module-finished.html", context)
    else:
        context.update({
            "DEBUG": settings.DEBUG,
            "module": m,
            "q": q,
            "prompt": q.render_prompt(task.get_answers_dict()),
            "answer": Answer.objects.filter(task=task, question_id=q.id).first(),

            "answer_module": Module.load(q.module_id) if q.module_id else None,
            "answer_tasks": Task.objects.filter(project=task.project, module_id=q.module_id),
            "answer_tasks_show_user": Task.objects.filter(project=task.project).exclude(editor=request.user).exists(),
            "answer_task": Task.objects.filter(is_answer_of__question_id=q.id),
        })
        return render(request, "question.html", context)

@login_required
def send_invitation(request):
    import email_validator
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    try:
        if not request.POST['user_id'] and not request.POST['user_email']:
            raise ValueError("Select a team member or enter an email address.")

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
            into_discussion=None, # TODO + validation request.POST.get("into_discussion"),

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
