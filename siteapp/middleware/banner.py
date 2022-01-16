from django.http.response import HttpResponseRedirect
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth import logout


class BannerMiddleware:

    BANNER_ENABLED = True

    def __init__(self, get_response):
        # Will load banner middleware if template is provided in branding or another template loader        
        try:
            get_template("warning_message.html")
        except TemplateDoesNotExist:
            self.BANNER_ENABLED = False
        self.get_response = get_response

    def __call__(self, request):
        # Code that is executed in each request before the view is called
        if self.BANNER_ENABLED:
            banner_url = "/warningmessage/"
            
            if request.user.is_authenticated and request.path == "/decline/":
                logout(request)
                return HttpResponseRedirect("/")

            if request.user.is_authenticated and request.path != banner_url:
                if not request.session.get("_banner_checked"):   
                    return HttpResponseRedirect(banner_url)  

        response = self.get_response(request)
        # Code that is executed in each request after the view is called
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_exception(self, request, exception):
        # This code is executed if an exception is raised
        pass

    def process_template_response(self, request, response):
        # This code is executed if the response contains a render() method
        return response