from django.http.response import HttpResponseRedirect
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth import logout

from django.shortcuts import redirect
from django.contrib import messages

class ErrorMiddleware:

    def __init__(self, get_response):
       self.get_response = get_response

    def __call__(self, request):
        # Code that is executed in each request before the view is called
        response = self.get_response(request)
        
        # Code that is executed in each request after the view is called
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_exception(self, request, exception):
        # This code is executed if an exception is raised
        messages.add_message(request, messages.ERROR, f"Error: {exception}")
        # return HttpResponseRedirect("/controls/components")
        return redirect(request.META.get('HTTP_REFERER'))

    def process_template_response(self, request, response):
        # This code is executed if the response contains a render() method
        return response