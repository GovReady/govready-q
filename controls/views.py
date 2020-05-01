from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from .oscal import Catalog, Catalogs
import json
import re
from .utilities import *
from .models import Statement, Element, System, CommonControl, CommonControlProvider



def test(request):
    # Simple test page of routing for controls
    output = "Test works."
    html = "<html><body><p>{}</p></body></html>".format(output)
    return HttpResponse(html)

def index(request):
    """Index page for controls"""

    # Get catalog
    catalog = Catalog()
    cg_flat = catalog.get_flattended_controls_all_as_dict()
    control_groups = catalog.get_groups()
    context = {
        "catalog": catalog,
        "control": None,
        "common_controls": None,
        "control_groups": control_groups
    }
    return render(request, "controls/index.html", context)

def catalogs(request):
    """Index page for catalogs"""

    context = {
        "catalogs": Catalogs(),
    }
    return render(request, "controls/index-catalogs.html", context)

def catalog(request, catalog_key):
    """Index page for controls"""

    # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattended_controls_all_as_dict()
    control_groups = catalog.get_groups()
    context = {
        "catalog": catalog,
        "control": None,
        "common_controls": None,
        "control_groups": control_groups
    }
    return render(request, "controls/index.html", context)

def group(request, catalog_key, g_id):
    """Temporary index page for catalog control group"""

     # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattended_controls_all_as_dict()
    control_groups = catalog.get_groups()
    group =  None
    # Get group/family of controls
    for g in control_groups:
        if g['id'].lower() == g_id:
            group = g
            break

    context = {
        "catalog": catalog,
        "control": None,
        "common_controls": None,
        "control_groups": control_groups,
        "group": group
    }
    return render(request, "controls/index-group.html", context)

def control(request, catalog_key, cl_id):
    """Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattended_controls_all_as_dict()

    # Handle properly formatted control id that does not exist
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", { "control": {} })

    # Get and return the control
    context = {
        "catalog": catalog,
        "control": cg_flat[cl_id.lower()]
    }
    return render(request, "controls/detail.html", context)

def editor(request, system_id, catalog_key, cl_id):
    """System Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get control catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattended_controls_all_as_dict()
    # If control id does not exist in catalog
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", { "control": {} })

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related statements if owner has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve any related CommonControls
        common_controls = CommonControl.objects.filter(oscal_ctl_id=cl_id)
        ccp_name = None
        if common_controls:
            cc = common_controls[0]
            ccp_name = cc.common_control_provider.name
        # Get and return the control

        # Retrieve any related Implementation Statements
        impl_smts = Statement.objects.filter(sid=cl_id)
        context = {
            "system": system,
            "catalog": catalog,
            "control": cg_flat[cl_id.lower()],
            "common_controls": common_controls,
            "ccp_name": ccp_name,
            "impl_smts": impl_smts
        }
        return render(request, "controls/editor.html", context)
    else:
        # User does not have permission to this system
        raise Http404

def editor_compare(request, system_id, catalog_key, cl_id):
    """System Control detail view"""

    cl_id = oscalize_control_id(cl_id)

    # Get control catalog
    catalog = Catalog(catalog_key)
    cg_flat = catalog.get_flattended_controls_all_as_dict()
    # If control id does not exist in catalog
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", { "control": {} })

    # Retrieve identified System
    system = System.objects.get(id=system_id)
    # Retrieve related statements if owner has permission on system
    if request.user.has_perm('view_system', system):
        # Retrieve any related CommonControls
        common_controls = CommonControl.objects.filter(oscal_ctl_id=cl_id)
        ccp_name = None
        if common_controls:
            cc = common_controls[0]
            ccp_name = cc.common_control_provider.name
        # Get and return the control

        # Retrieve any related Implementation Statements
        impl_smts = Statement.objects.filter(sid=cl_id)
        context = {
            "system": system,
            "catalog": catalog,
            "control": cg_flat[cl_id.lower()],
            "common_controls": common_controls,
            "ccp_name": ccp_name,
            "impl_smts": impl_smts
        }
        return render(request, "controls/editor-compare.html", context)
    else:
        # User does not have permission to this system
        raise Http404

# @task_view
def save_smt(request):
    """Save a statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
        # EXAMPLE CODE FOR GUARDIAN PERMISSIONS
        # # does user have write privs?
        # # if not task.has_write_priv(request.user):
        # #     return HttpResponseForbidden()

        # # validate question
        # # q = task.module.questions.get(id=request.POST.get("question"))

        # # validate and parse value
        # # if request.POST.get("method") == "clear":
        # #     # Clear means that the question returns to an unanswered state.
        # #     # This method is only offered during debugging to make it easier
        # #     # to test the application's behavior when questions are unanswered.
        # #     value = None
        # #     cleared = True
        # #     skipped_reason = None
        # #     unsure = False

        # # elif request.POST.get("method") == "skip":
        # #     # The question is being skipped, i.e. answered with a null value,
        # #     # because the user doesn't know the answer, it doesn't apply to
        # #     # the user's circumstances, or they want to return to it later.
        # #     value = None
        # #     cleared = False
        # #     skipped_reason = request.POST.get("skipped_reason") or None
        #     unsure = bool(request.POST.get("unsure"))

        #print(dict(request.POST))
        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]

        # Updating or saving a new statement?
        if len(form_values['smt_id']) > 0:
            # Look up existing Statement object
            statement = Statement.objects.get(pk=form_values['smt_id'])
            if statement is None:
                # Statement from received has an id no longer in the database.
                # Report error. Alternatively, in future save as new Statement object
                statement_status = "error"
                statement_msg = "The id for this statement is no longer valid in the database."
                return JsonResponse({ "status": "error", "message": statement_msg })
            # Update existing Statement object with received info
            statement.body = form_values['body']
            statement.remarks = form_values['remarks']
        else:
            # Create new Statement object
            statement = Statement(  sid=form_values['sid'], # need to make oscalized?
                sid_class=form_values['sid_class'],
                body=form_values['body'],
                statement_type=form_values['statement_type'],
                remarks=form_values['remarks'],
                )
        # Save Statement object
        try:
            statement.save()
            statement_status = "ok"
            statement_msg = "Statement saved."
        except Exception as e:
            statement_status = "error"
            statement_msg = "Statement save failed. Error reported {}".format(e)
            return JsonResponse({ "status": "error", "message": statement_msg })

        # Updating or saving a new producer_element?
        try:
            # Does the name match and existing element? (Element names are unique.)
            # TODO: Sanitize data entered in form?
            producer_element, created = Element.objects.get_or_create(name=form_values['producer_element_name'])
            # producer_element = Element(  name=form_values['producer_element_name'], )
            # ONLY save produce_element when creating a new producer element
            print("get_or_create result ", producer_element, created)
            # if (created == True):
            #     producer_element.save()
            producer_element_status = "ok"
            producer_element_msg = "Producer Element saved."
        except Exception as e:
            producer_element_status = "error"
            producer_element_msg = "Producer Element save failed. Error reported {}".format(e)
            return JsonResponse({ "status": "error", "message": producer_element_msg })

        # Associate Statement and Producer Element
        # TODO Only associate if we have created new statement object.
        try:
            statement.producer_element = producer_element
            statement.save()
            statement_element_status = "ok"
            statement_element_msg = "Statement associated with Producer Element."
        except Exception as e:
            statement_element_status = "error"
            statement_element_msg = "Failed to associate statement with Producer Element {}".format(e)
            return JsonResponse({ "status": "error", "message": statement_msg + " " + producer_element_msg + " " +statement_element_msg })

    # Serialize saved data object(s) to send back to update web page
    # The submitted form needs to be updated with the object primary keys (ids)
    # in order that future saves will be treated as updates.
    from django.core import serializers
    serialized_obj = serializers.serialize('json', [ statement, ])

    # Return successful save result to web page's Ajax request
    return JsonResponse({ "status": "success", "message": statement_msg + " " + producer_element_msg + " " +statement_element_msg, "statement": serialized_obj })

def delete_smt(request):
    """Delete a statement"""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    else:
        # check permissions
        # EXAMPLE CODE FOR GUARDIAN PERMISSIONS
        # # does user have write privs?
        # # if not task.has_write_priv(request.user):
        # #     return HttpResponseForbidden()

        # # validate question
        # # q = task.module.questions.get(id=request.POST.get("question"))

        # # validate and parse value
        # # if request.POST.get("method") == "clear":
        # #     # Clear means that the question returns to an unanswered state.
        # #     # This method is only offered during debugging to make it easier
        # #     # to test the application's behavior when questions are unanswered.
        # #     value = None
        # #     cleared = True
        # #     skipped_reason = None
        # #     unsure = False

        # # elif request.POST.get("method") == "skip":
        # #     # The question is being skipped, i.e. answered with a null value,
        # #     # because the user doesn't know the answer, it doesn't apply to
        # #     # the user's circumstances, or they want to return to it later.
        # #     value = None
        # #     cleared = False
        # #     skipped_reason = request.POST.get("skipped_reason") or None
        #     unsure = bool(request.POST.get("unsure"))

        #print(dict(request.POST))
        form_dict = dict(request.POST)
        form_values = {}
        for key in form_dict.keys():
            form_values[key] = form_dict[key][0]

        # Delete statement?
        statement = Statement.objects.get(pk=form_values['smt_id'])
        if statement is None:
            # Statement from received has an id no longer in the database.
            # Report error. Alternatively, in future save as new Statement object
            statement_status = "error"
            statement_msg = "The id for this statement is no longer valid in the database."
            return JsonResponse({ "status": "error", "message": statement_msg })
        # Save Statement object
        try:
            statement.delete()
            statement_status = "ok"
            statement_msg = "Statement deleted."
        except Exception as e:
            statement_status = "error"
            statement_msg = "Statement delete failed. Error reported {}".format(e)
            
        return JsonResponse({ "status": "error", "message": statement_msg }) 