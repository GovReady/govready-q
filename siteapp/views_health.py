import subprocess #nosec

from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    html = (
        '<html><body><ul>'
        '<li><a href="/health/check-system">check-system</a> - View OS health (from "top").</li>'
        '<li><a href="/health/check-vendor-resources">check-vendor-resources</a> - Checksum fetched vendor resources.</li>'
        '<li><a href="/health/list-vendor-resources">list-vendor-resources</a> - List fetched vendor resources.</li>'
        '<li><a href="/health/load-base">load-base</a> - Load base page template with toggleable libraries. Use "all" or "none" link at bottom of page, or edit URL to change which libraries are loaded.</li>'
        '<li><a href="/health/request-headers">request-headers</a> - View HTTP headers present in request sent by web browser.</li>'
        '</body></html>' )
    return HttpResponse(html)

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

def load_base(request, args):
    args = args.split(",")
    context = {'args': args}
    return render(request, 'base-conditional.html', context)

def request_headers(request):
    from pprint import pformat
    output = pformat({k:v for k,v in request.headers.items()})
    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)
