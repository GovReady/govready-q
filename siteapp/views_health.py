import subprocess #nosec

from django.http import HttpResponse

def check_system(request):
    output = subprocess.check_output(["./check-system.sh"]).decode("utf-8")
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)

def check_vendor_resources(request):
    output = subprocess.check_output(["./check-vendor-resources.sh"]).decode("utf-8")
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)

def list_vendor_resources(request):
    output = subprocess.check_output(["./list-vendor-resources.sh"]).decode("utf-8")
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)
