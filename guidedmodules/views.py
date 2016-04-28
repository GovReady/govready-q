from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from questions import Module
from .models import Task, Answer

@login_required
def new_task(request):
    # Create a new task.
    m = Module.load(request.GET['module'])
    task = Task.objects.create(user=request.user, module_id=m.id, title=m.title)
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
            "module": m,
            "q": q,
            "last_value": answered.get(q.id),
        })



