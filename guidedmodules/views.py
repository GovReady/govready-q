from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from questions import Module
from .models import Task, Answer

@login_required
def next_question(request):
    # Load the questions module.
    import rtyaml
    m = Module(rtyaml.load(open("sample_module.yaml")))

    # Get the Task.
    task, isnew = Task.objects.get_or_create(
        user=request.user,
        module_id=m.id)

    # Load the answers the user has saved so far.
    answered = { }
    for q in task.answer_set.all():
        answered[q.question_id] = q.value

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



