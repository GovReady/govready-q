# Generate screenshots of the application using a headless browser
# for creating test artifacts and documentation.
#
# A throw-away test database is used so that this command cannot see any existing
# user data and database changes are not persistent.
#
# Examples:
#
# Create screenshots for the FISMA Level app:
# ./manage.py test_screenshots --app-source '{ "type": "git", "url": "https://github.com/GovReady/govready-apps-dev", "path": "apps" }' \
#                              --app fisma_level \
#                              --path screenshots.pdf
#
# Create screenshots for authoring a new app and set
# (approximate) output image size:
# /manage.py test_screenshots --author-new-app \
#                             --path screenshots.pdf \
#                             --size 1024x768

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.crypto import get_random_string

from guidedmodules.models import Task
from siteapp.models import User, Organization, Project

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import os
import os.path
import re
import tempfile
from time import sleep

class Command(BaseCommand):
    help = 'Generate screenshots using Selenium.'

    def add_arguments(self, parser):
        parser.add_argument('--org-name', metavar='name', nargs='?', default="The Company, Inc.", help="The name of the temporary Organization that will be created.")
        parser.add_argument('--app-source', metavar='{source JSON}', nargs='?', help="The AppSource definition in JSON.")
        parser.add_argument('--app', metavar='{source/}app', nargs='?', help="The AppSource slug plus app name of a compliance app to fill out, or if --app-source is given then just the app name.")
        parser.add_argument('--test', metavar='testid', nargs='?', help="The ID of the test to run defined in the app's app.yaml 'tests' key.")
        parser.add_argument('--author-new-app', action="store_true", help="Take screenshots for Q documentation showing how to author a new compliance app.")
        parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', help="The path to write screenshots into, either a directory or a filename ending with .pdf.")
        parser.add_argument('--size', metavar='WIDTHxHEIGHT', nargs='?', help="The width and height, in pixels, of the headless web browser window.")

    def handle(self, *args, **options):
        # Fix up some settings.
        self.fixup_django_settings()

        # Start the headless browser.
        self.start_headless_browser(options['size'])

        # Prepare for taking screenshots.
        self.init_screenshots(options)

        # Switch to the throw-away database.
        from django.test.utils import setup_databases, teardown_databases
        dbinfo = setup_databases(True, False)

        # Initialize the database.
        from guidedmodules.management.commands.load_modules import Command as load_modules
        load_modules().handle()

        try:
            # Create a user and organization.
            self.init_user_organization(options)

            # Run a script on the headless browser, generating
            # a bunch of screenshots.
            if options['app']:
                self.screenshot_app(options)

            if options['author_new_app']:
                self.screenshot_author_new_app(options)

            # Combine images into a  PDF.
            if self.write_pdf_filename:
                self.write_pdf()
        finally:
            teardown_databases(dbinfo, 1)
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

    def start_headless_browser(self, geometry):
        # Initialize Selenium using our wrapper around Django's
        # StaticLiveServerTestCase.
        from siteapp.tests import SeleniumTest
        if geometry:
            SeleniumTest.window_geometry = geometry.split("x")
        SeleniumTest.setUpClass()
        self.browser = SeleniumTest()
        self.browser.setUp()

    def stop_headless_browser(self):
        from siteapp.tests import SeleniumTest
        self.browser.tearDown()
        self.browser = None
        SeleniumTest.tearDownClass()

    def init_user_organization(self, options):
        # Make a new user so that we have the credentials to log the user in.
        # We use a randomly generated password so that even if the script is
        # run on a non-test system and the test database creation somehow
        # fails, we haven't left a User in the database with insecure
        # credentials. The password will be thrown away when this process
        # terminates.
        self.temporary_user_random_password = get_random_string(24)
        self.user = User.objects.create(
            username="screenshots-user-{}".format(get_random_string(6)),
            email="test+user@q.govready.com")
        self.user.set_password(self.temporary_user_random_password)
        self.user.save()
        
        # Create a new Organization with the temporary user as the org's admin.
        self.org = Organization.create(
            subdomain="test-screenshots-"+get_random_string(6).lower(),
            name=options['org_name'],
            admin_user=self.user)

        # Add an AppSource if the user specified one.
        if options['app_source']:
            import json
            from guidedmodules.models import AppSource
            src_spec = json.loads(options['app_source'])
            self.app_source = AppSource.objects.create(
                slug=get_random_string(8),
                spec=src_spec
            )

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

        # Add a black border to saved images because screenshot
        # backgrounds are close to white and are typically shown
        # on white pages and that doesn't look good.
        from PIL import Image, ImageOps
        im = Image.open(fn)
        ImageOps\
            .expand(im, border=1, fill='black')\
            .save(fn)

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

    # BROWSER SESSION SCRIPTS

    def screenshot_app(self, options):
        # Start an app and answer its questions using test answers defined
        # in the app's module.

        # Log in.
        self.login()

        # Screenshot the homepage.
        self.browser.navigateToPage(self.org.subdomain, "/")
        self.screenshot("home")

        # Ok click the "Add other app" button.
        self.click_with_screenshot("#new-project", "home-new-app")

        # Start the app.
        self.screenshot("compliance_apps_catalog")
        self.click_with_screenshot(".app[data-app='" + self.app_source.slug + "/" + options['app'] + "'] button.view-app", "compliance_catalog_app") # TODO: Mixing into CSS selector.
        self.click_with_screenshot("#start-project", "start_" + options['app'].replace("/", "_"))

        # Get the Project instance that was just created.
        import urllib.parse
        s = urllib.parse.urlsplit(self.browser.browser.current_url)
        m = re.match(r"/projects/(\d+)/.*", s.path)
        assert m
        project = Project.objects.get(id=m.group(1))

        # Begin answering questions.
        def answer_task(task, test):
            # Get the answers to start answering.
            assert isinstance(test, dict)
            answers = test.get('answers', {})
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
            tests = project.root_task.module.spec.get('tests', {})
            assert isinstance(tests, dict)
            test = tests.get(options['test'], { "answers": {} })
            assert isinstance(test, dict)

            # Get the answers to start answering.
            answers = test.get('answers')
            assert isinstance(answers, dict)

            # Since this is a project, each answer is a sub-task that
            # needs to be started.
            for question in project.root_task.module.questions.all():
                # Start it.
                self.click_with_screenshot("#question-" + question.key, question.key)

                # Get the Task we just created,
                s = urllib.parse.urlsplit(self.browser.browser.current_url)
                m = re.match(r"/tasks/(\d+)/.*", s.path)
                assert m
                task = Task.objects.get(id=m.group(1))
                
                # Fill out the questions.
                answer_task(task, answers.get(question.key, {}))

                # Return to the project page.
                self.browser.navigateToPage(self.org.subdomain, project.get_absolute_url())
        

        # Kick if off.
        answer_project(project)

        # Take a final screenshot.
        self.screenshot("done")

    def screenshot_author_new_app(self, options):
        # Demonstrate how to author a new compliance app.

        # DEBUG has to be on for authoring tools, but
        # Django Debug Toolbars should be disabled.
        from django.conf import settings
        from siteapp import settings_application
        settings.DEBUG = True
        settings_application.DISABLE_DJANGO_DEBUG_TOOLBAR = True

        # Authoring tools also require that the user
        # have the guidedmodules.change_module permission.
        from guidedmodules.models import Module
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission
        self.user.user_permissions.add(Permission.objects.get(content_type=ContentType.objects.get_for_model(Module), codename='change_module'))

        # Log in.
        self.login()

        # Screenshot the homepage, click on "Add other app".
        self.browser.navigateToPage(self.org.subdomain, "/")
        self.click_with_screenshot("#new-project", "home")

        # Screenshot the app catalog.
        self.screenshot("catalog")

        # Create a new local path AppSource to store the new app.
        # Do this after the catalog is first screenshotted because
        # the catalog is cached by source, so by adding the source
        # after we don't have to worry about the new app being
        # cached.
        with tempfile.TemporaryDirectory() as appsrcpath:
            from guidedmodules.models import AppSource
            local_app_source = AppSource.objects.create(
                slug=get_random_string(8),
                spec={
                    "type": "local",
                    "path": appsrcpath,
                }
            )

            # Start a new compliance app.
            from guidedmodules.management.commands.compliance_app import Command as compliance_app
            app_name = "myfirstapp"
            compliance_app().handle(appsource=local_app_source.slug, appname=app_name, path=None)

            # Reload page.
            self.browser.navigateToPage(self.org.subdomain, "/store")

            # Screenshot the catalog again with the new app in it.
            self.screenshot("catalog_with_app", cursor_at=".app[data-app='" + local_app_source.slug + "/" + app_name + "']") # TODO: Mixing into CSS selector.

            # Utility class to create a with-block object
            # that opens a YAML file, returns the parsed value,
            # and then on exit writes the modified YAML value back
            # to the file.
            from guidedmodules.management.commands.compliance_app import EditYAMLFileInPlace
            class EditAppFile(EditYAMLFileInPlace):
                def __init__(self, fn):
                    super().__init__(os.path.join(appsrcpath, app_name, fn))

            # Edit app catalog information and reload.
            with EditAppFile("app.yaml") as app:
                app['catalog']['description']['short'] = "Achieve compliance for our organization's systems."

            # Force clear catalog cache.
            local_app_source.spec["bust_cache"] = 1
            local_app_source.save()

            # Reload & screengrab, and start app.
            self.browser.navigateToPage(self.org.subdomain, "/store")
            self.click_with_screenshot(".app[data-app='" + local_app_source.slug + "/" + app_name + "'] button.start-app", "start") # TODO: Mixing into CSS selector.

            # Screengrab app.
            self.screenshot("app")

            # Edit the app.
            with EditAppFile("app.yaml") as app:
                app['questions'][0]['title'] = "Start Compliance"

            # Start authoring tools.
            self.click_with_screenshot("#open-authoring-tools", "authoring-tool-link")
            self.browser.browser.execute_script("authoring_tool_reload_app_confirm=false")
            self.click_with_screenshot("#authoring-tools-reload-app", "authoring-tools-reload")
            sleep(1) # ajax...
            project_url = self.browser.browser.current_url

            # Go to sub-module.
            self.click_with_screenshot("#question-example form", "reload")
            self.screenshot("question")

            # Edit question.
            with EditAppFile("example.yaml") as app:
                app['questions'][0]['prompt'] = "What is your *least* favorite science fiction franchise?"

            # Go back to project, reload app, return to the question.
            self.browser.browser.get(project_url)
            self.browser.click_element("#open-authoring-tools")
            self.browser.browser.execute_script("authoring_tool_reload_app_confirm=false")
            self.browser.click_element("#authoring-tools-reload-app")
            sleep(1) # wait for ajax to cause page to be reloaded
            self.browser.click_element("#question-example > a")
            self.screenshot("revised-question")

            # Edit using in-browser tool.
            self.click_with_screenshot("#show_question_authoring_tool", "click_authoring_tool")
            self.screenshot("question-authoring-tool")
            self.browser.click_element("#question_authoring_tool button[data-dismiss=\"modal\"]") # clear modal

            # Answer question.
            self.browser.click_element("#question input[value=startrek]")
            self.browser.click_element("#save-button")
            sleep(1) # wait for AJAX redirect
            self.screenshot("module-finished")
