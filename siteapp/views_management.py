import subprocess #nosec

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

def index(request):
    html = (
        '<html><body><ul>'
        '<li><a href="/management/example">example</a> - example management command.</li>'
        '<li><a href="/health/check-vendor-resources">check-vendor-resources</a> - Checksum fetched vendor resources.</li>'
        '<li><a href="/health/list-vendor-resources">list-vendor-resources</a> - List fetched vendor resources.</li>'
        '<li><a href="/health/load-base">load-base</a> - Load base page template with toggleable libraries. Use "all" or "none" link at bottom of page, or edit URL to change which libraries are loaded.</li>'
        '<li><a href="/health/request-headers">request-headers</a> - View HTTP headers present in request sent by web browser.</li>'
        '<li><a href="/health/request">request</a> - View entire request (must have DEBUG set).</li>'
        '</body></html>' )
    return HttpResponse(html)

def example(request):
    # output = subprocess.check_output(["./check-system.sh"]).decode("utf-8")
    html = f"<html><body><pre>EXAMPLE Command</pre></body></html>"
    return HttpResponse(html)

# def check_vendor_resources(request):
#     output = subprocess.check_output(["./check-vendor-resources.sh"]).decode("utf-8")
#     html = "<html><body><pre>{}</pre></body></html>".format(output)
#     return HttpResponse(html)

