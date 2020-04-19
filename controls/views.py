from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from .oscal import Catalog, Catalogs
import json
import re
from .utilities import *
from .models import CommonControl, CommonControlProvider


def test(request):
    # Simple test page of routing for controls
    output = "Test works."
    html = "<html><body><p>{}</p></body></html>".format(output)
    return HttpResponse(html)

def control1(request, cl_id):
    """Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get catalog
    catalog = Catalog()
    cg_flat = catalog.get_flattended_controls_all_as_dict()

    # Handle properly formatted control id that does not exist
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", { "control": {} })

    # Get and return the control
    context = {
        "control": cg_flat[cl_id.lower()]
    }
    return render(request, "controls/detail.html", context)

def editor(request, cl_id):
    """Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get catalog
    catalog = Catalog()
    cg_flat = catalog.get_flattended_controls_all_as_dict()

    # Handle properly formatted control id that does not exist
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", { "control": {} })

    # Retrieve any related CommonControls
    common_controls = CommonControl.objects.filter(oscal_ctl_id=cl_id)
    ccp_name = None
    if common_controls:
        cc = common_controls[0]
        ccp_name = cc.common_control_provider.name
    # Get and return the control
    context = {
        "control": cg_flat[cl_id.lower()],
        "common_controls": common_controls,
        "ccp_name": ccp_name

    }
    return render(request, "controls/editor.html", context)

# @task_view
def save_smt(request):
    """Save a statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
    # does user have write privs?
    # if not task.has_write_priv(request.user):
    #     return HttpResponseForbidden()

    # validate question
    # q = task.module.questions.get(id=request.POST.get("question"))

    # validate and parse value
    # if request.POST.get("method") == "clear":
    #     # Clear means that the question returns to an unanswered state.
    #     # This method is only offered during debugging to make it easier
    #     # to test the application's behavior when questions are unanswered.
    #     value = None
    #     cleared = True
    #     skipped_reason = None
    #     unsure = False

    # elif request.POST.get("method") == "skip":
    #     # The question is being skipped, i.e. answered with a null value,
    #     # because the user doesn't know the answer, it doesn't apply to
    #     # the user's circumstances, or they want to return to it later.
    #     value = None
    #     cleared = False
    #     skipped_reason = request.POST.get("skipped_reason") or None
    #     unsure = bool(request.POST.get("unsure"))
        print(request.POST)
        value = request.POST.getlist("value")
        print("received POST data: ", value) # DEBUG

    # elif request.POST.get("method") == "save":
    #     # load the statement from the HTTP request
    #     value = request.POST.getlist("value")
    #     print("received POST data: ", value) # DEBUG

    #     # parse & validate
    #     try:
    #         pass
    #     except ValueError as e:
    #         # client side validation should have picked this up
    #         return JsonResponse({ "status": "error", "message": str(e) })

    return JsonResponse({ "status": "success", "message": str(value) })


