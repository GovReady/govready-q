import os

from django.http import HttpResponse

def check_system(request):
    output = os.popen("./check-system.sh").read()
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)

def check_vendor_resources(request):
    output = ''
    output = os.popen("./check-vendor-resources.sh").read()
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)

def list_vendor_resources(request):
    output = os.popen("./list-vendor-resources.sh").read()
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)
