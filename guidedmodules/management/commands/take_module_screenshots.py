from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

import os, time, subprocess, json, collections
import urllib.parse
from datetime import datetime

from guidedmodules.models import Task

import tqdm
from fpdf import FPDF

class Command(BaseCommand):
    help = 'Takes screenshots of every page of a module.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--geometry', default="1024x768", type=lambda s : [int(x) for x in s.split('x', 1)],
            help="Browser window size as WIDTHxHEIGHT in pixels.",
            metavar="1024x768")
        parser.add_argument(
            'fixture',
            help="A fixture to load containing a user, organization, and modules.",
            metavar="filename")
        parser.add_argument(
            'project_question',
            help="The ID of the question in the project to begin.",
            metavar="id")

    def with_test_server(func):
        def g(self, *args, **kwargs):
            # Start test server.
            test_server = subprocess.Popen(["./manage.py", "testserver",
                kwargs["fixture"]])

            # Set the baseurl.
            self.server_url = "http://test.localhost:8000"

            # Run wrapped function.
            try:
                return func(self, *args, **kwargs)
            finally:
                # Terminate test server.
                test_server.terminate()
        return g

    def with_selenium(func):
        def g(self, *args, **kwargs):
            # Start Selenium.
            import selenium.webdriver
            os.environ['PATH'] += ":/usr/lib/chromium-browser" # 'chromedriver' executable needs to be in PATH
            self.browser = selenium.webdriver.Chrome()
            self.browser.set_window_size(*kwargs['geometry']) # small desktop size

            # Run wrapped function.
            try:
                return func(self, *args, **kwargs)
            finally:
                # Kill Selenium.
                self.browser.quit()
        return g

    def fill_field(self, css_selector, text):
        self.browser.find_element_by_css_selector(css_selector).send_keys(text)
    def click_element(self, css_selector):
        self.browser.find_element_by_css_selector(css_selector).click()

    def with_parsed_fixture(func):
        def g(self, *args, **kwargs):
            # Parse the fixture to get what to answer for each question.
            self.objects = collections.defaultdict(lambda : {})
            for item in json.load(open(kwargs["fixture"])):
                self.objects[item['model']][item['pk']] = item['fields']
            return func(self, *args, **kwargs)
        return g


    @with_parsed_fixture
    @with_test_server
    @with_selenium
    def handle(self, *args, **options):
        # Map (module_key, question_key) pairs to ModuleQuestion field data.
        questions = {}
        for qobj in self.objects['guidedmodules.modulequestion'].values():
            m = self.objects['guidedmodules.module'][qobj['module']]['key']
            questions[(m, qobj['key'])] = qobj

        browser = self.browser

        # Wait until test server seems to be running.
        import selenium.common.exceptions
        while True:
            try:
                self.browser.get(self.url("/"))
                self.browser.find_element_by_css_selector("#id_login")
                time.sleep(1)
            except selenium.common.exceptions.NoSuchElementException:
                self.browser.get("data:text/html,waiting for server...")
                continue
            else:
                break

        # set this up after we wait for the server to start
        self.browser.implicitly_wait(3) # seconds

        # log in
        browser.get(self.url("/"))
        self.click_element("#djHideToolBarButton")
        self.fill_field("#id_login", "test")
        self.fill_field("#id_password", "1234")
        self.click_element("form.login button")
        time.sleep(1)

        # start a new project
        browser.get(self.url("/store"))
        self.fill_field("#id_title", "Test Project")
        self.click_element("#id_module_id_0") # first available project type
        self.click_element("button.btn-success")

        # project intro page
        self.click_element("#continue-btn")

        # start task
        self.click_element('#question-' + options['project_question'] + ' form a')

        # Initialize the PDF to have the same aspect ratio as the browser window,
        # at U.S. letter page width.
        pdf = FPDF(unit="in", format=[8.5, 8.5*options['geometry'][1]/options['geometry'][0]])

        # Loop through questions, saving screenshots.
        image_ctr = 0
        while True:
            # Use the debug strings to determine what module and question we're
            # looking at.
            try:
                module_key = self.browser.find_element_by_css_selector('#debug-module-key').text
                question_key = self.browser.find_element_by_css_selector('#debug-question-key').text

                # Get the question spec.
                spec = json.loads(questions[(module_key, question_key)]['spec'])
            except:
                # We're on the last page - there is no question.
                spec = None

            # Answer the question.
            if spec is None:
                # This is the last page.
                pass

            elif spec["type"] in ("interstitial", "external-function"):
                # Just click go!
                pass

            elif spec["type"] in ("text", "email-address", "url", "password", "longtext",
                "integer", "real"):
                # Get value from specification.
                test_value = spec.get('test-value')
                if test_value is None:
                    if spec["type"] in ("text", "password", "longtext"):
                        test_value = "test value"
                    elif spec["type"] == "email-address":
                        test_value = "test-value@govready.com"
                    elif spec["type"] == "url":
                        test_value = "https://www.govready.com"
                    elif spec["type"] == "integer":
                        test_value = 10
                    elif spec["type"] == "real":
                        test_value = 2.71828
                self.fill_field('#inputctrl', str(test_value))

            elif spec["type"] == "date":
                test_value = spec.get('test-value', datetime.now().date().isoformat())
                test_value_year, test_value_month, test_value_day = test_value.split('-', 3)
                self.fill_field('#question select[name=value_month]', test_value_month)
                self.fill_field('#question select[name=value_day]', test_value_day)
                self.fill_field('#question select[name=value_year]', test_value_year)

            elif spec["type"] in ("choice", "yesno"):
                test_value = spec.get('test-value')
                if test_value is None:
                    if spec["type"] == "choice":
                        # If no test-value is specified, then choose
                        # the first choice.
                        test_value = spec["choices"][0]["key"]
                    elif spec["type"] == "yesno":
                        # If no test-value is specified, then choose
                        # yes.
                        test_value = "yes"

                for input_elem in self.browser.find_elements_by_css_selector('#question input[name=value]'):
                    if input_elem.get_attribute("value") == test_value:
                        input_elem.click()

            elif spec["type"] == "multiple-choice":
                test_values = spec.get('test-value')
                if test_values is None:
                    # If no test-value is specified, then choose
                    # the first choice.
                    test_values = [spec["choices"][0]["key"]]

                for input_elem in self.browser.find_elements_by_css_selector('#question input[name=value]'):
                    if input_elem.get_attribute("value") in test_values:
                        input_elem.click()

            else:
                # TODO: file, module
                raise ValueError("Unimplemented question type: %s" % spec["type"])

            # Take the screenshot.

            # FPDF gets confused if we reuse the same filename?
            fn = ("/tmp/screen-%d.png" % image_ctr)
            image_ctr += 1
            browser.save_screenshot(fn)
            time.sleep(1)

            # Add to PDF, delete the temporary image file.
            pdf.add_page()
            pdf.image(fn, 0,0, 8.5,8.5*options['geometry'][1]/options['geometry'][0]) # width = page width
            os.unlink(fn)

            # If this was the module finished page, we're done.
            if spec is None:
                break

            # Save the answer and move to the next question.
            self.click_element("#save-button")

            # Wait until the page has re-loaded.
            self.browser.execute_script("window.has_not_reloaded = true")
            while True:
                if not self.browser.execute_script("return window.has_not_reloaded || false"):
                    break
                time.sleep(.1)

        # Save PDF.
        pdf.output("module.pdf", "F")

    def url(self, path):
        return urllib.parse.urljoin(self.server_url, path)
