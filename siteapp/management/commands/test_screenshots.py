# Generate screenshots of the application using a headless browser
# for creating test artifacts and documentation.
#
# This tool is meant to be run in a local development environment
# or as a part of a build/test pipeline. It uses your existing
# local database configuration to create a temporary test user
# account and project data. Therefore, do not run this script on a
# production server.

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.crypto import get_random_string

from guidedmodules.models import Task
from siteapp.models import User, Organization, Project

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import os
import os.path
import random
import re
from time import sleep

class Command(BaseCommand):
    help = 'Generate screenshots using Selenium.'

    def add_arguments(self, parser):
        parser.add_argument('--org-name', metavar='name', nargs='?', default="The Company, Inc.", help="The name of the temporary Organization that will be created.")
        parser.add_argument('--org', metavar='subdomain', nargs='?', help="The subdomain of an existing Organization to use.")
        parser.add_argument('--app', metavar='source/app', nargs='?', help="The AppSource slug plus app name of a compliance app to fill out.")
        parser.add_argument('--test', metavar='testid', nargs='?', help="The ID of the test to run defined in the app's app.yaml 'tests' key.")
        parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', help="The path to write screenshots into, either a directory or a filename ending with .pdf.")

    def handle(self, *args, **options):
        # Fix up some settings.
        self.fixup_django_settings()

        # Start the headless browser.
        self.start_headless_browser()

        # Prepare for taking screenshots.
        self.init_screenshots(options)

        # Create a user and organization.
        self.init_user_organization(options)

        try:
            # Run a script on the headless browser, generating
            # a bunch of screenshots.
            if options['app']:
                self.screenshot_app(options)

            # Combine images into a  PDF.
            if self.write_pdf_filename:
                self.write_pdf()
        finally:
            self.reset_database()
            self.stop_headless_browser()

    # STARTUP/SHUTDOWN UTILITY FUNCTIONS
        
    def fixup_django_settings(self):
        from django.conf import settings

        # Always turn debug off for screenshots.
        settings.DEBUG = False

        # Enable the mouse cursor following helper so that we see a fake
        # mouse cursor in the screenshots to indicate where clicks are
        # being made/simulated.
        settings.MOUSE_CURSOR_FOLLOWER = True

    def start_headless_browser(self):
        # Initialize Selenium using our wrapper around Django's
        # StaticLiveServerTestCase.
        from siteapp.tests import SeleniumTest
        SeleniumTest.setUpClass()
        self.browser = SeleniumTest()
        self.browser.setUp()

    def stop_headless_browser(self):
        from siteapp.tests import SeleniumTest
        self.browser.tearDown()
        self.browser = None
        SeleniumTest.tearDownClass()

    def init_user_organization(self, options):
        # No database records we create here should live beyond
        # this script. A database transaction would be handy, but
        # the LiveServerTestCase uses a different database connection
        # than what we have, and so it won't see the current transaction.
        self.objects_to_kill = []

        # Make a new user so that we have the credentials to log the user in.
        # We use a randomly generated password so that even if the script is
        # run on a non-test system, and if the database cleanup step at the
        # end fails, we haven't left a User in the database with insecure
        # credentials. The password will be thrown away when this process
        # terminates.
        self.temporary_user_random_password = get_random_string(24)
        self.user = User.objects.create(
            username="screenshots-user-{}".format(random.randint(10000, 99999)),
            email="test+user@q.govready.com")
        self.user.set_password(self.temporary_user_random_password)
        self.user.save()
        self.objects_to_kill.append(self.user)
        
        # Get the organization that will be used.
        if options['org']:
            # Use the specified org that already exists in the database.
            self.org = Organization.objects.get(subdomain=options['org'])

            # Add the user to the Organization.
            from siteapp.models import ProjectMembership
            pm, isnew = ProjectMembership.objects.get_or_create(user=self.user, project=self.org.get_organization_project())
            pm.is_admin = True
            pm.save()
            self.objects_to_kill.append(pm)
        else:
            # Create a new Organization with the temporary user as the org's admin.
            self.org = Organization.create(
                subdomain="test-screenshots-"+get_random_string(6).lower(),
                name=options['org_name'],
                admin_user=self.user)
            self.objects_to_kill.append(self.org)

        # Killing the user now requires first killing their org-specific account settings project.
        self.objects_to_kill.append(self.user.get_account_project(self.org))

    def init_screenshots(self, options):
        # Prepare for taking screenshots.
        self.screenshot_basepath = options['path']
        self.write_pdf_filename = None
        if options['path'].lower().endswith(".pdf"):
            self.write_pdf_filename = options['path']
            self.screenshot_basepath += "-temp"
        self.screenshot_image_filenames = []

    def write_pdf(self):
        # Write PDF.
        from fpdf import FPDF
        from PIL import Image
        dpi = 120 # note for calcs below that "pt" units are 1/72th of an inch
        pdf = FPDF(unit="pt")
        for image in self.screenshot_image_filenames:
            # Size the next PDF page to the size of this image.
            with open(image, "rb") as f:
                im = Image.open(f)
                page_size = im.size[0]/dpi*72, im.size[1]/dpi*72
            pdf.add_page(format=page_size)
            pdf.image(image, 0,0, page_size[0], page_size[1])
        pdf.output(self.write_pdf_filename, "F")

        # Delete the temporary directory of images.
        import shutil
        shutil.rmtree(self.screenshot_basepath)

    def reset_database(self):
        # Kill temporary objects.
        for obj in reversed(self.objects_to_kill):
            obj.delete()

    # SCRIPT UTILITY FUNCTIONS

    def screenshot(self, slug, cursor_at=None):
        # Take a screenshot of the current browser window.
        #
        # `slug` is appended to the filename to give generated image files
        # a descriptive name.
        #
        # If cursor_at, a CSS selector, is set, then position the fake mouse
        # cursor in the middle of the selected element to indicate where a
        # click is about to be performed.

        # Move the fake cursor.
        if cursor_at:
            elem = self.browser.browser.find_element_by_css_selector(cursor_at)
            self.browser.browser.execute_script("moveMouseToElem(arguments[0]);", elem)
            self.browser.browser.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });", elem)
            sleep(.1)

        # Make the output directory, construct the output filename,
        # and save the screenshot there. Remember the filename for
        # forming a PDF at the end.
        os.makedirs(self.screenshot_basepath, exist_ok=True)
        fn = os.path.join(
            self.screenshot_basepath,
            "{:03d}_{}.png".format(len(self.screenshot_image_filenames)+1, slug)
            )
        self.browser.browser.save_screenshot(fn)
        self.screenshot_image_filenames.append(fn)

    def click_with_screenshot(self, selector, slug):
        self.screenshot(slug, cursor_at=selector)
        self.browser.click_element(selector)

    def login(self):
        # Log the temporary user in.
        self.browser.navigateToPage(self.org.subdomain, "/")
        assert "Home" in self.browser.browser.title
        self.browser.fill_field("#id_login", self.user.username)
        self.browser.fill_field("#id_password", self.temporary_user_random_password)
        self.browser.click_element("form button.primaryAction")

        # Set their display name so the site header shows a nicer name than their email address.
        self.browser.click_element('#user-menu-dropdown'); sleep(.1)
        self.browser.click_element('#user-menu-account-settings'); sleep(.1)
        assert "Introduction | GovReady Account Settings" in self.browser.browser.title
        self.browser.click_element("#save-button"); sleep(.2) # intro page
        # Now at the what is your name page?
        self.browser.fill_field("#inputctrl", "User") # user's display name
        self.browser.click_element("#save-button"); sleep(.25)

    # GENERIC SCRIPT FOR STARTING AN APP AND ANSWERING ITS QUESTIONS

    def screenshot_app(self, options):
        # Start an app and answer its questions using test answers defined
        # in the app's module.

        # Log in.
        self.login()

        # Go to the app catalog.
        self.browser.navigateToPage(self.org.subdomain, "/store")
        self.screenshot("compliance_catalog")

        # Start the app.
        self.click_with_screenshot(".app[data-app='" + options['app'] + "'] button.view-app", "compliance_catalog_app") # TODO: Mixing into CSS selector.
        self.click_with_screenshot("#start-project", "start_app")

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

                # Take screenshot. Save answer, which redirects to next question
                # via AJAX. Since it's asynchronous, Selenium won't wait for the
                # next page to load.
                cur_url = self.browser.browser.current_url # see below
                self.click_with_screenshot(button_selector, task.module.module_name + "-" + question.key)

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
                self.click_with_screenshot("#question-" + key, key)

                # Get the Task we just created and mark it for deletion later,
                s = urllib.parse.urlsplit(self.browser.browser.current_url)
                m = re.match(r"/tasks/(\d+)/.*", s.path)
                assert m
                task = Task.objects.get(id=m.group(1))
                self.objects_to_kill.append(task)
                
                # Fill out the questions.
                answer_task(task, value)

                # Return to the project page.
                self.browser.navigateToPage(self.org.subdomain, project.get_absolute_url())
        

        # Kick if off.
        answer_project(project)

        # Take a final screenshot.
        self.screenshot("done")
