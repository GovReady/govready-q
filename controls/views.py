from django.shortcuts import render
from django.http import HttpResponse
from .oscal import Catalog
import json
import re


def test(request):
    # Simple test page of routing for controls
    output = "Test works."
    html = "<html><body><p>{}</p></body></html>".format(output)
    return HttpResponse(html)

def control1(request, cl_id):
    """Control detail view"""

    # Handle improperly formatted control id
    # Recognize only properly formmated control id:
    #   at-1, at-01, ac-2.3, ac-02.3, ac-2 (3), ac-02 (3), ac-2(3), ac-02 (3)
    pattern = re.compile("^[A-Za-z][A-Za-z]-[0-9() .]*$")
    if not pattern.match(cl_id):
        return render(request, "controls/detail.html", { "control": {} })

    # Get catalog
    catalog = Catalog()
    cg_flat = catalog.get_flattended_controls_all_as_dict()

    # Handle properly formatted existing id
    # Transform various patterns of control ids into OSCAL format
    # Fix leading zero in at-01, ac-02.3, ac-02 (3)
    cl_id = cl_id = re.sub(r'^([A-Za-z][A-Za-z]-)0(.*)$', r'\1\2', cl_id)
    # Change paranthesis into a dot
    cl_id = re.sub(r'^([A-Za-z][A-Za-z]-)([0-9]*)([ ]*)\(([0-9]*)\)$', r'\1\2.\4', cl_id)
    # Remove trailing space
    cl_id = cl_id.strip(" ")

    # Handle properly formatted control id that does not exist
    if cl_id.lower() not in cg_flat:
        return render(request, "controls/detail.html", { "control": {} })

    # Get and return the control
    context = {
        "control": cg_flat[cl_id.lower()]
    }
    return render(request, "controls/detail.html", context)
