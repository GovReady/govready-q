from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from guidedmodules.models import Task
from siteapp.models import User, Organization, Project

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import random
import re
from time import sleep

class Command(BaseCommand):
    help = 'Generate screenshots using Selenium.'

    def add_arguments(self, parser):
        parser.add_argument('--org', metavar='subdomain', nargs='?', help="The subdomain of the Organization to use.")
        parser.add_argument('--app', metavar='source/app', nargs='?', help="The AppSource slug plus app name of a compliance app to fill out.")
        parser.add_argument('--test', metavar='testid', nargs='?', help="The ID of the test to run defined in the app's app.yaml 'tests' key.")
        parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', help="The path to write screenshots into, either a directory or a filename ending with .pdf.")

    def handle(self, *args, **options):
        # Fix up some settings. Always turn debug off for screenshots.
        from django.conf import settings
        settings.DEBUG = False

        # Initialize Selenium using our wrapper around Django's
        # StaticLiveServerTestCase.
        from siteapp.tests import SeleniumTest
        SeleniumTest.setUpClass()
        self.browser = SeleniumTest()
        self.browser.setUp()

        # Enable the mouse cursor following helper.
        settings.MOUSE_CURSOR_FOLLOWER = True

        # Get the organization that will be used.
        self.org = Organization.objects.get(subdomain=options['org'])
        self.subdomain = self.org.subdomain

        # No database records we create here should live beyond
        # this script. A database transaction would be handy, but
        # the LiveServerTestCase uses a different database connection
        # than what we have, and so it won't see the current transaction.
        self.objects_to_kill = []

        # Prepare for taking screenshots.
        self.screenshot_basepath = options['path']
        save_pdf = None
        if options['path'].lower().endswith(".pdf"):
            save_pdf = options['path']
            self.screenshot_basepath += "-temp"
        self.screenshot_image_filenames = []

        # Run the script.
        try:
            if options['app']:
                self.screenshot_app(options)

            # Generate PDF.
            if save_pdf:
                # Write PDF.
                from fpdf import FPDF
                from PIL import Image
                dpi = 120 # not that "pt" units are 1/72th of an inch
                pdf = FPDF(unit="pt")
                for image in self.screenshot_image_filenames:
                    # Size the next PDF page to the size of this image.
                    with open(image, "rb") as f:
                        im = Image.open(f)
                        page_size = im.size[0]/dpi*72, im.size[1]/dpi*72
                    pdf.add_page(format=page_size)
                    pdf.image(image, 0,0, page_size[0], page_size[1])
                pdf.output(save_pdf, "F")

                # Delete the temporary directory.
                import shutil
                shutil.rmtree(self.screenshot_basepath)

        finally:
            # Kill temporary objects.
            for obj in reversed(self.objects_to_kill):
                obj.delete()

            # Terminate the browser.
            self.browser.tearDown()
            self.browser = None
            SeleniumTest.tearDownClass()

    def screenshot(self, slug, cursor_at=None):
        if cursor_at:
            elem = self.browser.browser.find_element_by_css_selector(cursor_at)
            self.browser.browser.execute_script("moveMouseToElem(arguments[0]);", elem)
            self.browser.browser.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });", elem)
            sleep(.1)

        import os, os.path

        os.makedirs(self.screenshot_basepath, exist_ok=True)

        fn = os.path.join(
            self.screenshot_basepath,
            "{:03d}_{}.png".format(len(self.screenshot_image_filenames)+1, slug)
            )
        self.browser.browser.save_screenshot(fn)
        self.screenshot_image_filenames.append(fn)

    def login(self):
        # Make a new user so that we have the credentials to log the user in.
        self.user = User.objects.create(
            username="screenshots-user-{}".format(random.randint(10000, 99999)),
            email="test+user@q.govready.com")
        self.user.set_password("password")
        self.user.save()
        self.objects_to_kill.append(self.user)
        
        # Add them to the Organization.
        from siteapp.models import ProjectMembership
        pm, isnew = ProjectMembership.objects.get_or_create(user=self.user, project=self.org.get_organization_project())
        pm.is_admin = True
        pm.save()
        self.objects_to_kill.append(pm)

        # Killing the user now first requires killing their org settings project.
        self.objects_to_kill.append(self.user.get_account_project(self.org))

        # Log the user in.
        self.browser.naviateToPage(self.subdomain, "/")
        assert "Home" in self.browser.browser.title
        self.browser.fill_field("#id_login", self.user.username)
        self.browser.fill_field("#id_password", "password")
        self.browser.click_element("form button.primaryAction")

        # Set their display name so the site header shows a nicer name than their email address.
        self.browser.click_element('#user-menu-dropdown'); sleep(.1)
        self.browser.click_element('#user-menu-account-settings'); sleep(.1)
        assert "Introduction | GovReady Account Settings" in self.browser.browser.title
        self.browser.click_element("#save-button"); sleep(.2) # intro page
        # Now at the what is your name page?
        self.browser.fill_field("#inputctrl", "User") # user's display name
        self.browser.click_element("#save-button"); sleep(.25)


    def screenshot_app(self, options):
        # Create a test user and log them in.
        self.login()

        # Go to the app.
        self.browser.naviateToPage(self.subdomain, "/store/" + options['app'])
        self.screenshot("start_app", cursor_at="#start-project")

        # Start the app.
        self.browser.click_element("#start-project")

        # Get the Project instance that was just created.
        import urllib.parse
        s = urllib.parse.urlsplit(self.browser.browser.current_url)
        m = re.match(r"/projects/(\d+)/.*", s.path)
        assert m
        project = Project.objects.get(id=m.group(1))

        # Schedule it and its root task for deletion.
        self.objects_to_kill.append(project)
        self.objects_to_kill.append(project.root_task)

        # Begin answering questions.
        def answer_task(task, test):
            # Get the answers to start answering.
            assert isinstance(test, dict)
            answers = test.get('answers')
            assert isinstance(answers, dict)

            while True:
                # What question are we looking at?
                s = urllib.parse.urlsplit(self.browser.browser.current_url)
                m = re.match(r"/tasks/(\d+)/.*?/(question/(.*)|finished)$", s.path)
                assert m
                assert m.group(1) == str(task.id)
                if m.group(2) == "finished":
                    # We reached the end of this module.
                    self.screenshot(task.module.module_name + "-finished")
                    return

                # We're at a question. Answer it.
                question = task.module.questions.get(key=m.group(3))

                # If we have an answer for this question, fill it in.
                button_selector = "#save-button"
                if question.spec['type'] == "interstitial":
                    # Nothing to do.
                    pass
                elif question.key in answers:
                    # Fill in the answer.
                    answer = answers[question.key]
                    if question.spec['type'] in ('text', 'password', "email-address", "url", "integer", "real"):
                        self.browser.fill_field('#inputctrl', str(answer))
                    elif question.spec['type'] in ('longtext',):
                        self.browser.fill_field('#inputctrl', str(answer))
                    elif question.spec['type'] in ('date',):
                        raise Exception("not implemented")
                    elif question.spec['type'] in ('choice', 'yesno'):
                        # To make YAML definition easier...
                        if isinstance(answer, bool): answer = "yes" if answer else "no"
                        self.browser.click_element("#question input[value=" + str(answer) + "]") # TODO: Answer might not fit a valid CSS selector.
                    elif question.spec['type'] == 'multiple-choice':
                        assert isinstance(answer, list)
                        for choice in answer:
                            self.browser.click_element("#question input[value=" + str(choice) + "]") # TODO: Answer might not fit a valid CSS selector.
                    elif question.spec['type'] in ('file', 'module', 'module-set'):
                        raise Exception("not implemented")
                else:
                    button_selector = "#skip-button"

                # Take screenshot.
                self.screenshot(task.module.module_name + "-" + question.key, cursor_at=button_selector)

                # Sleep to make this process more appropriate for
                # capturing a video?
                #sleep(2)

                # Save answer, which redirects to next question.
                cur_url = self.browser.browser.current_url # see below
                self.browser.click_element(button_selector)

                # Since this is ajax, wait for page URL to change.
                while self.browser.browser.current_url == cur_url:
                    sleep(.5)

        def answer_project(project):
            # Get the test.
            tests = project.root_task.module.spec.get('tests')
            assert isinstance(tests, dict)
            assert options['test'] in tests
            test = tests[options['test']]
            assert isinstance(test, dict)

            # Get the answers to start answering.
            answers = test.get('answers')
            assert isinstance(answers, dict)

            # Since this is a project, each answer is a sub-task that
            # needs to be started.
            for key, value in answers.items():
                # Start it.
                self.screenshot(key, cursor_at="#question-" + key)
                self.browser.click_element("#question-" + key)

                # Get the Task we just created and mark it for deletion later,
                s = urllib.parse.urlsplit(self.browser.browser.current_url)
                m = re.match(r"/tasks/(\d+)/.*", s.path)
                assert m
                task = Task.objects.get(id=m.group(1))
                self.objects_to_kill.append(task)
                
                # Fill out the questions.
                answer_task(task, value)

                # Return to the project page.
                self.browser.naviateToPage(self.subdomain, project.get_absolute_url())
        

        # Kick if off.
        answer_project(project)

        # Take a final screenshot.
        self.screenshot("done")
