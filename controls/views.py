from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from .oscal import Catalog, Catalogs
import json
import re
from .utilities import *
from .models import Statement, Element, CommonControl, CommonControlProvider



def test(request):
    # Simple test page of routing for controls
    output = "Test works."
    html = "<html><body><p>{}</p></body></html>".format(output)
    return HttpResponse(html)

def index(request):
    # Temporary index page for controls
    output = "Temporary index page for controls. Please <a href='800-53/ac-1/'>view AC-1</a> to start."
    html = "<html><body><p>{}</p></body></html>".format(output)
    # return HttpResponse(html)

    # cl_id = oscalize_control_id(cl_id)

    # Get catalog
    catalog = Catalog()
    cg_flat = catalog.get_flattended_controls_all_as_dict()

    # # Handle properly formatted control id that does not exist
    # if cl_id.lower() not in cg_flat:
    #     return render(request, "controls/detail.html", { "control": {} })

    # Retrieve any related CommonControls
    # common_controls = CommonControl.objects.filter(oscal_ctl_id=cl_id)
    # ccp_name = None
    # if common_controls:
    #     cc = common_controls[0]
    #     ccp_name = cc.common_control_provider.name
    # Get and return the control

    context = {
        "control": None,
        "common_controls": None,
    }
    return render(request, "controls/index.html", context)



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

        #print(dict(request.POST))
        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]
        print(form_values)

        # Save Statement
        try:
            statement = Statement(  sid=form_values['sid'], # need to make oscalized?
                                    sid_class=form_values['sid_class'],
                                    body=form_values['body'],
                                    statement_type=form_values['statement_type'],
                                    remarks=form_values['remarks'],
                                 )
            statement.save()
            statement_status = "ok"
            statement_msg = "Statement saved."
        except Exception as e:
            statement_status = "error"
            statement_msg = "Statement save failed. Error reported {}".format(e)
            return JsonResponse({ "status": "error", "message": statement_msg })

        # Save element (e.g., component) if received
        if 'element' in form_values and form_values['element'] is not None:
            if Element.objects.filter(name=form_values['element']).exists():
                # Does Element already exist?
                # TODO need better filtering -- should pick element in form with auto complete
                elements = Element.objects.filter(name=form_values['element'])
                element = elements[0]
                element_status = "ok"
                element_msg = "Element exists."
            else:
                # Create Element
                try:
                    element = Element(name=form_values['element'])
                    element.save()
                    print(element)
                    element_status = "ok"
                    element_msg = "Element saved."
                except Exception as e:
                    element_status = "error"
                    element_msg = "Element save failed. Error reported {}".format(e)
                    return JsonResponse({ "status": "error", "message":  statement_msg + " " + element_msg })
        else:
            print("problem with element")

        print("element", element)
        # Associate element with statement
        try:
            statement.elements.add(element)
            statement_element_status = "ok"
            statement_element_msg = "Statement associated with element."
        except Exception as e:
            statement_element_status = "error"
            statement_element_msg = "Failed to associate statement with element {}".format(e)
            return JsonResponse({ "status": "error", "message": statement_msg + " " + element_msg + " " +statement_element_msg })


    return JsonResponse({ "status": "success", "message": statement_msg + " " + element_msg + " " +statement_element_msg })


