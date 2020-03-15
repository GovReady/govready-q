import subprocess #nosec

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

def index(request):
    html = (
        '<html><body><ul>'
        '<li><a href="/health/check-system">check-system</a> - View OS health (from "top").</li>'
        '<li><a href="/health/check-vendor-resources">check-vendor-resources</a> - Checksum fetched vendor resources.</li>'
        '<li><a href="/health/list-vendor-resources">list-vendor-resources</a> - List fetched vendor resources.</li>'
        '<li><a href="/health/load-base">load-base</a> - Load base page template with toggleable libraries. Use "all" or "none" link at bottom of page, or edit URL to change which libraries are loaded.</li>'
        '<li><a href="/health/request-headers">request-headers</a> - View HTTP headers present in request sent by web browser.</li>'
        '<li><a href="/health/request">request</a> - View entire request (must have DEBUG set).</li>'
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

    if hasattr(request, 'headers'):
        # Django >= 2.2
        output = pformat({k:v for k,v in request.headers.items()})
    else:
        # Django < 2.2
        # FYI, this code doesn't look for Content-Length and Content-Type, just HTTP_*
        import re
        regex = re.compile('^HTTP_')
        output = pformat(
            dict((regex.sub('', header), value) for (header, value) in
            request.META.items() if header.startswith('HTTP_'))
        )

    html = "<html><body><pre>{}</pre></body></html>".format(output)
    return HttpResponse(html)

def request(request):
    if settings.DEBUG:
        from pprint import pformat
        output = pformat(vars(request))
        html = "<html><body><pre>{}</pre></body></html>".format(output)
    else:
        html = "<html><body><p>Please set DEBUG and try again.</p></body></html>"
    return HttpResponse(html)
