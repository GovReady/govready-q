from django.shortcuts import render
from django.http import HttpResponse
from controls.seccontrol import SecControl
from controls.seccontrol import SecControlsAll
import json


def test(request):
    # Simple test page of routing for controls
    output = "Test works."
    html = "<html><body><p>{}</p></body></html>".format(output)
    return HttpResponse(html)

def control1(request, ctlid):
    """Control detail view"""
    sc = SecControl(ctlid.upper())
    output = "SEC Control\n {}".format(sc.get_control_json())
    context = {
        "control": sc,
    }
    print("DEBUG: context: {}".format(context))
    return render(request, "controls/detail.html", context)

