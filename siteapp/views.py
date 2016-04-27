from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from questions import Module

def homepage(request):
    # Load the questions module.
    import rtyaml
    m = Module(rtyaml.load(open("sample_module.yaml")))
    answered = request.session.get('answers', { })

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
        answered[q] = value
        request.session["answers"] = answered

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
            "q": q,
            "last_value": answered.get(q.id),
        })



