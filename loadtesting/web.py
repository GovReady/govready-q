import logging
import requests
import structlog
import parsel
from random import sample
import re

from django.test import Client

from django.test import RequestFactory
from siteapp.urls import urlpatterns

from django.urls.exceptions import Resolver404 as Resolver404

from siteapp.models import *
from guidedmodules.models import *

logging.basicConfig()
logger = get_logger()

class WebClient():
    session = None
    response = None
    selector = None
    base_url = None
    projects = None
    comp_links = None
    current_url = ''

    def __init__(self, username, org_slug):
        self.user = User.objects.get(username=username)
        self.org = Organization.objects.get(slug=org_slug)

        self.session = RequestFactory()

    def _url(self, path):
        # currently a no-op function, but for debug purposes it is useful to be able to change path handling in one spot
        return path

    def _use_page(self, response):
        self.response = response
        if (self.response.status_code != 200):
            print("Got a non-200 response: {}".format(self.response.status_code))
            if (self.response.status_code == 302):
                print("proper URL: {}".format(self.response.url))
        self.selector = parsel.Selector(text=response.content.decode('utf-8'))
        self.html_debug(dir="/tmp/")

    def _resolve(self, req):
        # see https://stackoverflow.com/a/12011907
        # we might actually want to switch to the "test client" rather than RequstFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)

        self.current_url = req.path
        for url in urlpatterns:
            try:
                match = url.resolve(req.path[1:])
                if match:
                    self._use_page(match.func(req, *match.args, **match.kwargs))
                    return
            except Resolver404:
                logger.error(event="_resolve_path", msg="404: Failed to resolve url request path")
        raise Exception("{} not resolved".format(req.path))

    def load(self, path):
        url = self._url(path)
        print("GET on: <{}>".format(url))
        req = self.session.get(url)
        req.user = self.user
        req.organization = self.org
        self._resolve(req)


    def form_fields(self, css):
        return self.form_fields_by_ref(self.selector.css(css))
    def form_fields_by_ref(self, form):
        return dict([
            (x.xpath('@name').get(), x.xpath('@value').get())
            for x in form.css('input')
        ])

    def form(self, css, fields={}):
        form = self.selector.css(css)
        return self.form_by_ref(form, fields)

    def form_by_ref(self, form, fields={}):
        base_fields = self.form_fields_by_ref(form)
        for (key, val) in fields.items():
            base_fields[key] = val
        if 'action' in form.attrib:
            url = self._url(form.attrib['action'])
        else:
            url = self.base_url
        self.post(url, base_fields)

    def post(self, url, fields):
        print("POST on: <{}>".format(url))
        req = self.session.post(url, fields)
        req.user = self.user
        req.organization = self.org
        self._resolve(req)


    def add_system(self):
        portfolio = sample(list(self.user.portfolio_list()), 1)[0]
        print("Adding project to portfolio: {} (#{})".format(portfolio.title, portfolio.id))
        self.post("/store/govready-q-files-startpack/System-Description-Demo?portfolio={}".format(portfolio.id), {"organization":self.org.slug})
        print(self.response.url)

    def get_projects(self):
        if not self.projects:
            self.load('/projects')
            self.projects = self.selector.css('a::attr("href")').re('^/projects/.*')
        return self.projects

    def load_project(self):
        self.load(self.get_projects()[-1])
        

    def start_section_for_proj(self, id):
        url = Project.objects.get(id=id).get_absolute_url()
        self.load(url)
        all_forms = self.selector.css('form.start-task')
        if len(all_forms) == 0:
            return 0

        form = all_forms[0]
        self.form_by_ref(form)
        return len(all_forms)

    def load_task(self):
        self.load_project()
        task = sample([x.attrib['href'] for x in self.selector.css('.question-column [href^="/task"]')], 1)[0]
        self.load(task)

    # after loading a task
    def pick_section(self):
        section = sample(self.selector.css('.question'), 1)[0]
        if len(section.css('form')) > 0:
            self.form_by_ref(section.css('form')[0])
        elif len(section.css('[href^="/tasks/"]')) > 0:
            self.load(section.css('[href^="/tasks/"]').attrib['href'])
        else:
            print("something was missing here")

    def fill_questions(self):
        sel = '.row .form-group .form-control'
        form = self.selector.css(sel)

    def html_debug(self, filename="test.html", dir="siteapp/static/"):
        with open(dir + filename, 'w') as file:
            file.write(self.response.content.decode('utf-8'))
        #return self.response.url
        


