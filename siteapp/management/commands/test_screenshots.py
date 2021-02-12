# Generate screenshots of the application using a headless browser
# for creating test artifacts and documentation.
#
# A throw-away test database is used so that this command cannot see any existing
# user data and database changes are not persistent. However, it would not be
# advisable to run this command on a production system.
#
# Examples:
#
# Create screenshots for the FISMA Level app:
# ./manage.py test_screenshots --app-source '{ "slug": "govready-apps-dev", "type": "git", "url": "https://github.com/GovReady/govready-apps-dev", "path": "apps" }' \
#                              --app govready-apps-dev/fisma_level \
#                              --path screenshots.pdf
# The --app-source argument can be repeated multiple times if more than one AppSource
# is needed to run the script.
#
# Create screenshots for authoring a new app and set
# (approximate) output image size:
# ./manage.py test_screenshots --author-new-app \
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
import rtyaml

class Command(BaseCommand):
    help = 'Generate screenshots using Selenium.'

    def add_arguments(self, parser):
        parser.add_argument('--org-name', metavar='name', nargs='?', default="The Company, Inc.", help="The name of the temporary Organization that will be created.")
        parser.add_argument('--app-source', metavar='{source JSON}', action="append", help="An AppSource definition in JSON. This argument can be repeated.")
        parser.add_argument('--app', metavar='source/app', nargs='?', help="The AppSource slug plus app name of a compliance app to fill out.")
        parser.add_argument('--test', metavar='testid', nargs='?', help="The ID of the test to run defined in the app's app.yaml 'tests' key, or @filename to load a test from a YAML file.")
        parser.add_argument('--author-new-app', action="store_true", help="Take screenshots for Q documentation showing how to author a new compliance app.")
        parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', help="The path to write screenshots into, either a directory or a filename ending with .pdf.")
        parser.add_argument('--size', metavar='widthXheight', nargs='?', help="The width and height, in pixels, of the headless web browser window, or 'maximized'.")
        parser.add_argument('--mouse-speed', metavar='seconds', nargs='?', default="0", type=float, help="Each mouse move will have this duration.")

    def handle(self, *args, **options):
        # Fix up some settings.
        self.fixup_django_settings()

        # Start the headless browser.
        self.start_headless_browser(options['size'])
        self.mouse_speed = options["mouse_speed"]

        # Prepare for taking screenshots.
        if options['path']:
            self.init_screenshots(options)

        # Switch to the throw-away test database so no database records
        # we create in this command are persistent.
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
            if getattr(self, 'write_pdf_filename', None):
                self.write_pdf()
        finally:
            # Clean up the throw-away test database.
            teardown_databases(dbinfo, 1)

            # Close selenium.
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
            SeleniumTest.window_geometry = (geometry.split("x") if geometry != "maximized" else geometry)
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
        # credentials. The pwd will be thrown away when this process
        # terminates.
        self.temporary_user_random_password = get_random_string(24)
        self.user = User.objects.create(
            username="screenshots-user-{}".format(get_random_string(6)),
            email="test+user@q.govready.com")
        self.user.set_password(self.temporary_user_random_password)
        self.user.save()
        
        # Create a new Organization with the temporary user as the org's admin.
        self.org = Organization.create(
            slug="test-screenshots-"+get_random_string(6).lower(),
            name=options['org_name'],
            admin_user=self.user)

        # Add AppSources specified by the user.
        for spec in (options['app_source'] or []):
            import json
            from guidedmodules.models import AppSource
            try:
                src_spec = json.loads(spec)
                if not isinstance(src_spec, dict): raise ValueError()
            except ValueError as e:
                raise ValueError("Invalid value for --app-source '{}': {}".format(spec, e))
            app_source = AppSource.objects.create(
                slug=src_spec.get("slug") or get_random_string(8),
                spec=src_spec
            )
            print("Created AppSource", app_source, "=>", app_source.get_description())

    def init_screenshots(self, options):
        # Prepare for taking screenshots.
        self.screenshot_basepath = options['path']
        self.write_pdf_filename = None
        if self.screenshot_basepath.lower().endswith(".pdf"):
            self.write_pdf_filename = self.screenshot_basepath
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

    def fill_field(self, field, value):
        self.browser.fill_field(field, value)
        sleep(self.mouse_speed)

    def move_cursor_to(self, elem):
        elem = self.browser.browser.find_element_by_css_selector(elem)
        sleep(self.mouse_speed * .25) # pause before the next motion
        self.browser.browser.execute_script("moveMouseToElem(arguments[0], arguments[1]);", elem, self.mouse_speed)
        scrollTop0 = self.browser.browser.execute_script("return $(window).scrollTop()")
        while not self.browser.browser.execute_script("return moveMouseToElem_finished"): sleep(.1) # wait for mouse movement animation to complete
        sleep(.1 + self.mouse_speed * .5) # pause so the user can see where the mouse ended up before we click
        scrollTop1 = self.browser.browser.execute_script("return $(window).scrollTop()")
        if scrollTop0 != scrollTop1:
            sleep(self.mouse_speed * .5) # pause extra if the window scrolled
        self.browser.browser.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });", elem)

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
            self.move_cursor_to(cursor_at)

        # Make the output directory, construct the output filename,
        # and save the screenshot there. Remember the filename for
        # forming a PDF at the end.
        if not hasattr(self, 'screenshot_basepath'): return # no screenshots are requested
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

    def click_element(self, elem):
        self.move_cursor_to(elem)
        self.browser.click_element(elem)

    def click_with_screenshot(self, selector, slug):
        self.screenshot(slug, cursor_at=selector)
        self.browser.click_element(selector)

    def login(self):
        # speed up this part
        old_mouse_speed = self.mouse_speed
        self.mouse_speed = 0

        # Log the temporary user in.
        self.browser.navigateToPage("/")
        assert "Home" in self.browser.browser.title
        self.fill_field("#id_login", self.user.username)
        self.fill_field("#id_password", self.temporary_user_random_password)
        self.click_element("form button.primaryAction")

        # Set their display name so the site header shows a nicer name than their email address.
        self.click_element('#user-menu-dropdown'); sleep(.1)
        self.click_element('#user-menu-account-settings'); sleep(.1)
        assert "Introduction | GovReady Account Settings" in self.browser.browser.title
        self.click_element("#save-button"); sleep(.2) # intro page
        # Now at the what is your name page?
        self.fill_field("#inputctrl", "User") # user's display name
        self.click_element("#save-button"); sleep(.25)

        # restore setting
        self.mouse_speed = old_mouse_speed

    # BROWSER SESSION SCRIPTS

    def screenshot_app(self, options):
        # Start an app and answer its questions using test answers defined
        # in the app's module.

        # Log in.
        self.login()

        # Screenshot the homepage.
        self.browser.navigateToPage("/")
        self.screenshot("home")

        # Ok click the "Add other app" button.
        self.click_with_screenshot("#new-project", "home-new-app")

        # Start the app.
        self.screenshot("compliance_apps_catalog")
        self.click_with_screenshot(".app[data-app='" + options['app'] + "'] a.view-app", "compliance_catalog_app") # TODO: Mixing into CSS selector.
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
                    break

                # We're at a question. Answer it.
                question = task.module.questions.get(key=m.group(3))

                # If we have an answer for this question, fill it in.
                if question.spec['type'] == "interstitial":
                    # Nothing to do.
                    pass
                elif question.key in answers:
                    # Fill in the answer.
                    answer = answers[question.key]
                    if question.spec['type'] in ('text', 'password', "email-address", "url", "integer", "real"):
                        self.fill_field('#inputctrl', str(answer))
                    elif question.spec['type'] in ('longtext',):
                        self.fill_field('#inputctrl', str(answer))
                    elif question.spec['type'] in ('date',):
                        raise Exception("not implemented")
                    elif question.spec['type'] in ('choice', 'yesno'):
                        # To make YAML definition easier...
                        if isinstance(answer, bool): answer = "yes" if answer else "no"
                        self.click_element("#question input[value=" + repr(answer) + "]") # TODO: Answer might not fit a valid CSS selector.
                    elif question.spec['type'] == 'multiple-choice':
                        assert isinstance(answer, list)
                        for choice in answer:
                            self.click_element("#question input[value=" + repr(choice) + "]") # TODO: Answer might not fit a valid CSS selector.
                    elif question.spec['type'] == 'datagrid':
                        assert isinstance(answer, list)
                        for field in answer:
                            self.click_element("#question input[value=" + repr(field) + "]") # TODO: Answer might not fit a valid CSS selector.
                    elif question.spec['type'] in ('file', 'module', 'module-set'):
                        raise Exception("not implemented")
                else:
                    # Skip this question.
                    self.click_element('#no-idea-button')

                # Take screenshot. Save answer, which redirects to next question
                # via AJAX. Since it's asynchronous, Selenium won't wait for the
                # next page to load.
                cur_url = self.browser.browser.current_url # see below
                self.click_with_screenshot("#save-button", task.module.module_name + "-" + question.key)

                # Since this is ajax, wait for page URL to change.
                while self.browser.browser.current_url == cur_url:
                    sleep(.5)

            # Finished.
            for scroll_target in test.get("scroll-to", []):
                sleep(float(test["pause"]))
                self.browser.browser.execute_script("$('html, body').animate({ scrollTop: Math.max($(arguments[0]).offset().top-50, 0)}, 4000);", scroll_target)
            if test.get("pause"):
                sleep(float(test["pause"]))

        def answer_project(project, test):
            # Get the test.
            assert isinstance(test, dict)
            for step in test.get("steps", []):
                assert isinstance(step, dict)
                if step["type"] == "answer-questions":
                    # Get the answers and start answering all of the
                    # questions with those answers.
                    answer_project_questions(
                        project,
                        step.get('answers', {}))

        def answer_project_questions(project, answers):
            print("Running", project, "with answers:")
            print(rtyaml.dump(answers))
            print()

            # Since this is a project, each answer is a sub-task that
            # needs to be started.
            for question in project.root_task.module.questions.all():
                # Skip if not in the test.
                if question.key not in answers:
                    continue

                # Start it.
                self.click_with_screenshot("#question-" + question.key, question.key)
                sleep(.5)

                # Where did we go?
                if question.spec['type'] in ('module', 'module-set') and question.spec.get("protocol"):
                    inner_test = answers.get(question.key, {}).get('test', { })
                    if "/store" in self.browser.browser.current_url:
                        # This unanswered module-type question has a protocol, so we've been taken
                        # to the compliance apps catalog. Start the first app that we see.
                        css_filter = ""
                        inner_app_id = answers.get(question.key, {}).get('app', '')
                        if inner_app_id:
                            css_filter = "[data-app='" + inner_app_id + "']"
                        self.click_with_screenshot(".app{} a.view-app".format(css_filter), "compliance_catalog_app")
                        self.click_with_screenshot("#start-project", "start")
                        sleep(2) # scrolling to app
                        self.browser.browser.execute_script("$(window).scrollTop(0)") # go back to top

                        # We're now back at the original project.
                        # If there's no inner test data, don't do anything further.
                        if not inner_test:
                            continue

                        # Otherwise, click the question again to go
                        # to the Project that we started by starting an app.
                        self.click_with_screenshot("#question-" + question.key, question.key)

                    # We either just started the inner app or it already existed.
                    # What project was just created?
                    s = urllib.parse.urlsplit(self.browser.browser.current_url)
                    m = re.match(r"/projects/(\d+)/.*", s.path)
                    assert m
                    p = Project.objects.get(id=m.group(1))

                    # Get test data for the inner app.
                    inner_test = answers.get(question.key, {}).get('test', { "answers": {} })

                    # Run it.
                    answer_project(p, inner_test)

                    # At the end of the project, go back to the higher-up project.
                    self.click_with_screenshot('a.parent-project', "back")

                else:
                    # Get the inner test data for Task that we just clicked.
                    inner_test = answers.get(question.key, {})

                    # Get the Task we just created or navigated to,
                    s = urllib.parse.urlsplit(self.browser.browser.current_url)
                    m = re.match(r"/tasks/(\d+)/.*", s.path)
                    assert m
                    task = Task.objects.get(id=m.group(1))

                    # Fill out the questions.
                    answer_task(task, inner_test)

                    # Return to the project page.
                    self.browser.navigateToPage(project.get_absolute_url())
        

        # Get the test to run.
        if options['test'] and options['test'].startswith("@"):
            # Load from file.
            with open(options['test'][1:]) as f:
                test = rtyaml.load(f)
        else:
            # Load from app metadata.
            tests = project.root_task.module.spec.get('tests', {})
            assert isinstance(tests, dict)
            test = tests.get(options['test'], { "answers": {} })

        # Kick if off.
        answer_project(project, test)

        # Take a final screenshot.
        self.screenshot("done")

        # Let the user see how cool this was.
        sleep(self.mouse_speed*5)

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
        self.browser.navigateToPage("/")
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
            self.browser.navigateToPage("/store")

            # Screenshot the catalog again with the new app in it.
            self.screenshot("catalog_with_app", cursor_at=".app[data-app='" + local_app_source.slug + "/" + app_name + "']") # TODO: Mixing into CSS selector.

            # Utility class to create a with-block object
            # that opens a YAML file, returns the parsed value,
            # and then on exit writes the modified YAML value back
            # to the file.
            class EditAppFile(rtyaml.edit):
                def __init__(self, fn):
                    super().__init__(os.path.join(appsrcpath, app_name, fn))

            # Edit app catalog information and reload.
            with EditAppFile("app.yaml") as app:
                app['catalog']['description']['short'] = "Achieve compliance for our organization's systems."

            # Force clear catalog cache.
            local_app_source.spec["bust_cache"] = 1
            local_app_source.save()

            # Reload & screengrab, and start app.
            self.browser.navigateToPage("/store")
            self.click_with_screenshot(".app[data-app='" + local_app_source.slug + "/" + app_name + "'] button.start-app", "start") # TODO: Mixing into CSS selector.

            # Screengrab app.
            self.screenshot("app")

            # Edit the app.
            with EditAppFile("app.yaml") as app:
                app['questions'][0]['title'] = "Start Compliance"

            # Upgrade the app.
            self.click_with_screenshot("#upgrade-app", "upgrade app button")
            self.browser.browser.execute_script("upgrade_app_option_confirm=false")
            self.click_with_screenshot("#do-upgrade", "upgrade app page")
            sleep(1) # ajax...
            project_url = self.browser.browser.current_url

            # Go to sub-module.
            self.click_with_screenshot("#question-example form", "reload")
            self.screenshot("question")

            # Edit question.
            with EditAppFile("example.yaml") as app:
                app['questions'][0]['prompt'] = "What is your *least* favorite science fiction franchise?"

            # Go back to project, ugprade app, return to the question.
            self.browser.browser.get(project_url)
            self.click_with_screenshot("#upgrade-app", "upgrade app button")
            self.browser.browser.execute_script("upgrade_app_option_confirm=false")
            self.click_with_screenshot("#do-upgrade", "upgrade app page")
            sleep(1) # wait for ajax to cause page to be reloaded
            self.click_element("#question-example > a")
            self.screenshot("revised-question")

            # Edit using in-browser tool.
            self.click_with_screenshot("#show_question_authoring_tool", "click_authoring_tool")
            self.screenshot("question-authoring-tool")
            self.click_element("#question_authoring_tool button[data-dismiss=\"modal\"]") # clear modal

            # Answer question.
            self.click_element("#question input[value=startrek]")
            self.click_element("#save-button")
            sleep(1) # wait for AJAX redirect
            self.screenshot("module-finished")
