from django.shortcuts import render
from django.http import HttpResponse
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
