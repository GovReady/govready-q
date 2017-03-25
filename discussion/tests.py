from django.conf import settings
from siteapp.models import User, ProjectMembership, Organization
from siteapp.tests import SeleniumTest, var_sleep

from selenium.common.exceptions import NoSuchElementException

import os

class DiscussionTests(SeleniumTest):

    def setUp(self):
        super().setUp()

        # Load modules from the fixtures directory so that we have the required
        # modules as well as a test project.
        from guidedmodules.models import ModuleSource
        from guidedmodules.management.commands.load_modules import Command as load_modules
        ModuleSource.objects.create(
            namespace="fixture",
            spec={
                "type": "local",
                "path": "fixtures/modules/other",
            }
        )
        load_modules().handle()

        # Create a default user that is a member of the organization.

        self.user = User.objects.create(username="me")
        self.user.set_password("1234")
        self.user.save()

        # Create the Organization.

        org = Organization.create(name="Our Organization", subdomain="testorg",
            admin_user=self.user)

    def url(self, path):
        # Within this test, we only generate URLs for the organization subdomain.
        return super().url("testorg", path)

    def _login(self, username="me", password="1234"):
        # Fill in the login form and submit.
        self.browser.get(self.url("/"))

        self.assertRegex(self.browser.title, "Home")
        self.fill_field("#id_login", username)
        self.fill_field("#id_password", password)
        self.click_element("form button.primaryAction")

    def _new_project(self):
        self.browser.get(self.url("/projects"))
        self.click_element("#new-assessment")
        self.click_element(".assessment[data-assessment='fixture/simple_project']")
        self.click_element("#start-assessment")
        self.fill_field("#id_title", "My Simple Project")
        self.click_element("#start-assessment")
        var_sleep(1)
        self.assertRegex(self.browser.title, "My Simple Project")

    def _start_task(self):
        # Assumes _new_project() just finished.

        # Start the task.
        self.click_element('#question-simple_module .task-commands form.start-task a')

    def _accept_invitation(self, email):
        # Assumes an invitation email was sent.

        # Extract the URL in the email and visit it.
        invitation_body = self.pop_email().body
        invitation_url_pattern = re.escape(self.url("/invitation/")) + r"\S+"
        self.assertRegex(invitation_body, invitation_url_pattern)
        m = re.search(invitation_url_pattern, invitation_body)
        self.browser.get(m.group(0))

        # Since we're not logged in, we hit the invitation splash page.
        self.click_element('#button-sign-in')
        var_sleep(.5) # wait for page to load

        # We're at the sign-in page. Go to the create account page
        # and register. Use a random username so that we submit something
        # unique, since a test may create multiple users.
        self.assertRegex(self.browser.title, "Sign In")
        self.click_element("p a") # This isn't a very good targetting of the "sign up" link.
        var_sleep(.5) # wait for page to load
        self.fill_field("#id_username", "test+%d@q.govready.com" % random.randint(10000, 99999))
        self.fill_field("#id_email", email)
        self.fill_field("#id_password1", "1234")
        self.fill_field("#id_password2", "1234")
        self.click_element("form.signup button") # This isn't a very good targetting of the "sign up" link.
        var_sleep(.5) # wait for next page to load

        # Test that an allauth confirmation email was sent.
        self.assertIn("Please confirm your email address at GovReady Q by following this link", self.pop_email().body)

    def test_discussion(self):

        # Log in and create a new project.
        self._login()
        self._new_project()
        self._start_task()

        # Move past the introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5) # wait for page to reload

        # We're now on the first actual question.
        # Start a team conversation.
        self.click_element("#start-a-discussion a")
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
            'modules',
            'assets',
            'testimage.png'
        )

        self.fill_field("#discussion-attach-file", testFilePath)
        var_sleep(.5)
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
