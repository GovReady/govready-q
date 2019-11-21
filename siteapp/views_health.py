import subprocess #nosec

from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    output = subprocess.check_output(["./check-system.sh"]).decode("utf-8")
    html = (
        '<html><body><ul>'
        '<li><a href="/health/check-system">check-system</a></li>'
        '<li><a href="/health/check-vendor-resources">check-vendor-resources</a></li>'
        '<li><a href="/health/list-vendor-resources">list-vendor-resources</a></li>'
        '<li><a href="/health/load-base">load-base</a></li>'
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
    print(args)
    args = args.split(",")
    print(args)
    context = {'args': args}
    return render(request, 'base-conditional.html', context)
