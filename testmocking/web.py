import requests
import parsel
from random import sample
import re
from django.test import Client

class WebClient():
    session = None
    response = None
    selector = None
    base_url = None
    projects = None
    comp_links = None

    def __init__(self, base_url):
        match = re.search(r'^(https?://)?(?P<host>[^:/]+)', base_url)
        host = match['host']
        self.base_url = base_url

        self.session = Client(HTTP_HOST=host)
        print("web test client with host <{}>".format(host))

    def _url(self, path):
        # currently a no-op function, but for debug purposes it is useful to be able to change path handling in one spot
        return path

    def _use_page(self, response):
        self.response = response
        self.selector = parsel.Selector(text=str(response.content))
        print(str(self.response.content))
        print(str(self.response.status_code))
        print(self.response.serialize_headers())

    def load(self, path):
        url = self._url(path)
        print("GET on: <{}>".format(url))
        self._use_page(self.session.get(url, follow=True))


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
            url = self._url(form.attrib['action'])
        else:
            url = self.base_url
        print("POST on: <{}>".format(url))
        res = self.session.post(url, base_fields, follow=True)
        self._use_page(res)



    def add_system(self):
        # TODO see if this shouldn't be hardcoded
        self.load("/store")

        print(self.selector.css('body').get())
        print("testing")
        form = sample(self.selector.css('[action^="/store"]'), 1)[0]
        self.form_by_ref(form)
        print(self.response.url)
        #self.html_debug()

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
        


