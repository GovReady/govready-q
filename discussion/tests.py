from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Permission

from siteapp.models import User, ProjectMembership, Organization, Portfolio
from siteapp.tests import SeleniumTest, var_sleep

from selenium.common.exceptions import NoSuchElementException

import os

class DiscussionTests(SeleniumTest):

    def setUp(self):
        super().setUp()

        # Set screen resolution
        capabilities = {
         "resolution": "1920x1080"
        }

        # Load modules from the fixtures directory so that we have the required
        # modules as well as a test project.
        from guidedmodules.models import AppSource
        from guidedmodules.management.commands.load_modules import Command as load_modules

        AppSource.objects.all().delete()
        AppSource.objects.get_or_create(
              # this one exists on first db load because it's created by
              # migrations, but because the testing framework seems to
              # get rid of it after the first test in this class
            slug="system",
            is_system_source=True,
            defaults={
                "spec": { # required system projects
                    "type": "local",
                    "path": "fixtures/modules/system",
                }
            }
        )
        load_modules().handle() # load system modules

        AppSource.objects.create(
            slug="project",
            spec={
                "type": "local",
                "path": "fixtures/modules/other",
            }
        )\
        	.add_app_to_catalog("simple_project")

        # Create a default user that is a member of the organization.

        self.user_pw = get_random_string(4)
        self.user = User.objects.create(username="me")
        self.user.set_password(self.user_pw)
        self.user.save()
        # Grant user permission to view appsource
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))

        # Create the Organization.

        org = Organization.create(name="Our Organization", slug="testorg",
            admin_user=self.user)
        
        # Create a Portfolio and Grant Access
        portfolio = Portfolio.objects.create(title=self.user.username)
        portfolio.assign_owner_permissions(self.user)

    def _login(self):
        # Fill in the login form and submit.
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")
        self.click_element("li#tab-signin")
        self.fill_field("#id_login", self.user.username)
        self.fill_field("#id_password", self.user_pw)
        self.click_element("form#login_form button[type=submit]")
        self.assertRegex(self.browser.title, "Your Compliance Projects")

    def _new_project(self):
        self.browser.get(self.url("/projects"))
        self.click_element("#new-project")

        # Select Portfolio
        self.select_option_by_visible_text('#id_portfolio', self.user.username)
        self.click_element("#select_portfolio_submit")
        var_sleep(1)

        self.click_element(".app[data-app='project/simple_project'] .view-app")
        self.click_element("#start-project")
        var_sleep(1)
        self.assertRegex(self.browser.title, "I want to answer some questions on Q.")
        var_sleep(2.0)

    def _start_task(self):
        # Assumes _new_project() just finished.

        # Start the task.
        self.click_element('#question-simple_module')

    def test_discussion(self):

        # Log in and create a new project.
        self._login()
        self._new_project()
        var_sleep(.5) # wait for page to reload
        self._start_task()

        # Move past the introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.8) # wait for page to reload

        # Click interstital "Got it" button
        self.click_element("#save-button")
        var_sleep(.5)

        # We're now on the first actual question.
        # Start a team conversation.
        self.click_element("#start-a-discussion")
        self.fill_field("#discussion-your-comment", "Hello is anyone *here*?")
        var_sleep(.5)
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(.5)

        # Test Script injection
        self.fill_field("#discussion-your-comment",
            "<script id='injectiontest2'>document.getElementsByTagName('body')[0].appendChild('<div id=\\'injectiontest1\\'></div>');</script>")
        var_sleep(.5)
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(.5)

        # Check that the element was *not* added to the page.
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#injectiontest1')

        # Check that the script tag was removed entirely.
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#injectiontest2')

        # Test some special characters
        self.fill_field("#discussion-your-comment", "¥")
        var_sleep(.5)
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(.5)

        self.assertInNodeText("¥", '.comment[data-id="3"] .comment-text p')

        # Test file attachments

        # We need to upload a file that we know exists.
        testFilePath = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fixtures',
            'testimage.png'
        )

        self.fill_field("#discussion-attach-file", testFilePath)
        var_sleep(1)
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(1) # Give time for the image to upload.

        # Test that we have an image.
        img = self.browser.find_element_by_css_selector('.comment[data-id="4"] .comment-text p img')
        self.assertIsNotNone(img)

        # Test that the image actually exists.
        imageFile = img.get_attribute('src')

        result = self.browser.execute_script("""var http = new XMLHttpRequest();
            http.open('HEAD', '{}', false);
            http.send();
            return http.status!=404;""".format(imageFile))

        self.assertTrue(result)
