from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

import os, time
import urllib.parse

from guidedmodules.models import Task

import tqdm
from fpdf import FPDF

class Command(BaseCommand):
    help = 'Takes screenshots of every page of a module.'

    def handle(self, *args, **options):
        # Configuration.
        browser_size = (1100, 1400) # desktop width, enough height to capture what we need

        # Set up web driver.
        import selenium.webdriver
        os.environ['PATH'] += ":/usr/lib/chromium-browser" # 'chromedriver' executable needs to be in PATH
        browser = selenium.webdriver.Chrome()
        browser.implicitly_wait(3) # seconds
        browser.set_window_size(*browser_size) # small desktop size

        # Set up host and task.
        task = Task.objects.get(id=62)
        self.server_url = "http://%s.localhost:8000" % task.project.organization.subdomain

        # Which questions will we grab?
        answers = task.get_answers().with_extended_info()
        questions = [
            q.key
            for q in task.module.questions.order_by("definition_order")
            if q.key in answers.answers and q.key not in answers.was_imputed
        ]

        # Let the user log in.
        print("PLEASE LOG IN! :) YOU HAVE 9 SECONDS.")
        browser.get(self.url("/"))
        time.sleep(9)

        # Initialize the PDF to have the same dimensions as the browser window.
        pdf = FPDF(unit="in", format=[8.5, 8.5*browser_size[1]/browser_size[0]])

        # Ok iterate through the questions.
        image_files = set()
        for i, key in tqdm.tqdm(list(enumerate(questions))):
            # Navigate to the page and take a screenshot.
            browser.get("about:blank") # ensure we don't prematurely think the page is loaded
            browser.get(self.url(task.get_absolute_url() + "?q=" + urllib.parse.quote(key)))
            browser.find_element_by_css_selector("body") # wait until page is loaded
            time.sleep(.25) # not really necessary?

            # FPDF gets confused if we reuse the same filename?
            fn = ("/tmp/screen-%d.png" % i)
            browser.save_screenshot(fn)

            # Add to PDF.
            pdf.add_page()
            pdf.image(fn, 0,0, 8.5,8.5*browser_size[1]/browser_size[0]) # width = page width
            os.unlink(fn)

        # Save PDF.
        pdf.output("module.pdf", "F")

          


    def url(self, path):
        return urllib.parse.urljoin(self.server_url, path)
