from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings

from questions import Module
from .models import Project, ProjectMembership, Task, Answer, Invitation
from django.contrib.auth.models import User

@login_required
def new_project(request):
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
        user=request.user,
        project=project,
        module_id=m.id,
        title=m.title)
    return HttpResponseRedirect(task.get_absolute_url())

@login_required
def next_question(request, taskid, taskslug):
    # Get the Task.
    task = get_object_or_404(Task, user=request.user, id=taskid)

    # Redirect if slug is not canonical.
    if request.path != task.get_absolute_url():
        return HttpResponseRedirect(task.get_absolute_url())

    # Load the questions module.
    m = task.load_module()

    # Load the answers the user has saved so far.
    answered = task.get_answers_dict()

    # Process form data.
    if request.method == "POST":
        # validation
        q = request.POST.get("question")
        if q not in m.questions_by_id:
            return HttpResponse("invalid question id", status=400)
        value = request.POST.get("value", "")
        if not value.strip():
            return HttpResponse("empty answer", status=400)
        
        # save answer
        answer, isnew = Answer.objects.get_or_create(
            task=task,
            question_id=q)
        answer.value = value
        answer.save()

        # kick the task's updated field
        task.save(update_fields=[])

        # return to a GET request
        return HttpResponseRedirect(request.path)


    # Display requested question.
    if "q" in request.GET:
        q = m.questions_by_id[request.GET['q']]

    else:
        # Display next unanswered question.
        q = m.next_question(answered)

    if not q:
        return render(request, "module-finished.html", {
            "task": task,
            "m": m,
            "output": m.render_output(answered),
            "all_questions": filter(lambda q : not q.should_skip(answered), m.questions)
        })
    else:
        return render(request, "question.html", {
            "task": task,
            "module": m,
            "q": q,
            "prompt": q.render_prompt(task.get_answers_dict()),
            "last_value": answered.get(q.id),
            "can_ask_team_member": True,
            "can_ask_team_members_user_list": list(User.objects.all().exclude(id=request.user.id)),
            "team_member_responses": { t: t.answers.filter(question_id=q).first() for t in task.requests.all() },
        })

@login_required
def send_invitation(request):
    import email_validator
    if request.method != "POST": raise HttpResponseNotAllowed(['POST'])
    try:
        if not request.POST['user'] and not request.POST['email']:
            raise ValueError("Select a team member or enter an email address.")
        inv = Invitation.create(
            Task.objects.get(user=request.user, id=request.POST['task']),
            request.POST['question'],
            User.objects.get(id=request.POST['user']) if request.POST['user'] else None,
            email_validator.validate_email(request.POST['email'])["email"] if request.POST['email'] else None,
            request.POST['text'],
            request.POST['project'] == "true"
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
    return HttpResponseRedirect(inv.accept(request))
