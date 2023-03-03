import subprocess #nosec
import sys

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core import management


def print_http_response(f):
    """
    Wraps a python function that prints to the console, and
    returns those results as a HttpResponse (HTML)
    """

    class WritableObject:
        def __init__(self):
            self.content = []
        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(['<BR>' if c == '\n' else c for c in printed.content ])
    return new_f


def index(request):
    html = (
        '<html><body>'
        '<h3>Call Django management commands</h3>'
        '<ul>'
        '<li><a href="/management/listcomponents">manage.py listcomponents</a> - generate a list of components</li>'
        '</body></html>' )
    return HttpResponse(html)

def example(request):
    # output = subprocess.check_output(["./check-system.sh"]).decode("utf-8")
    html = f"<html><body><pre>EXAMPLE Command</pre></body></html>"
    return HttpResponse(html)

@print_http_response
def listcomponents(request):
    # output = subprocess.check_output(["./check-system.sh"]).decode("utf-8")
    # if user not admin:
    #     html = f"<html><body><pre>Page only available to admins</pre></body></html>"

    # user is admin, run command
    result = management.call_command('listcomponents')
    html = f"<html><body><pre>manage.py listcomponents\n {result}</pre></body></html>"
    return HttpResponse(html)
