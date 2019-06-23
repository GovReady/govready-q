import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

class Command(BaseCommand):
    client = None
    bad_comps = []

    help = 'Starts one or many assessments for an org'

    def add_arguments(self, parser):
        parser.add_argument('--base_url', type=str, required=True, help="")
        parser.add_argument('--username', type=str, required=True, help="")
        parser.add_argument('--password', type=str, required=True, help="")
        parser.add_argument('--to-completion', action="store_true", help="")

    def handle(self, *args, **options):
        self.client = WebClient(options['base_url'])
        self.client.load('')
        self.client.login(options['username'], options['password'])

        if options['to_completion']:
            comps = self.client.get_components()
            repeatable_comp_count = len(self.client.selector.css('.question-title .glyphicon-plus'))
            print("{} repeatable components".format(repeatable_comp_count))
            while options['to_completion'] and len(comps) > repeatable_comp_count + len(self.bad_comps):
                self._do_single()
                comps = self.client.get_components()
            print("{} repeatable components, {} non-completable components".format(repeatable_comp_count, len(self.bad_comps)))
        else:
            self._do_single()

    def _do_single(self):
        all = self.client.get_components()
        comp = sample(all, 1)[0]
        if len(all) > len(self.bad_comps):
            while comp in self.bad_comps:
                comp = sample(all, 1)[0]
        print(comp)
        self.client.load('/store?q=' + comp)
        url_before = self.client.response.url
        self.client.add_comp()
        url_after = self.client.response.url

        if url_before == url_after:
            self.bad_comps.append(comp)
            print("Got same URL, marking component {} as non-completable".format(comp))


import requests
import parsel
from random import sample

class WebClient():
    session = requests.Session()
    response = None
    selector = None
    base_url = None
    projects = None
    comp_links = None

    def __init__(self, base_url):
        self.base_url = base_url

    def _use_page(self, response):
        self.response = response
        self.selector = parsel.Selector(text=response.text)

    def load(self, path):
        self._use_page(self.session.get(self.base_url + path))

    def login(self, username, password):
        self.form('.login', {"login": username, "password": password})

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
            path = form.attrib['action']
        else:
            path = self.response.url.replace(self.base_url, '')
        res = self.session.post(self.base_url + path, base_fields)
        self._use_page(res)



    def add_system(self):
        # TODO see if this shouldn't be hardcoded
        self.load("/store?protocol=govready.com/apps/compliance/2018/information-technology-system")
        self.form('[action="/store/dev-apps/demo-generic-website"]')

    def get_projects(self):
        if not self.projects:
            self.load('/projects')
            self.projects = self.selector.css('a::attr("href")').re('^/projects/.*')
        return self.projects

    def load_project(self):
        self.load(self.get_projects()[-1])
        

    def get_components(self):
        self.load_project()
        self.comps_links = self.selector.css('form[method=get][action="/store"]').css('input::attr("value")').getall()
        return self.comps_links

    # this dumps you to the main project page after execution
    def add_comp(self):
        self.form('form[action^="/store"]')

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
            file.write(self.response.text)
        return self.response.url
        


