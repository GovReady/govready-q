from django.conf import settings
from django.test import SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from unittest import skip

import re

def var_sleep(float):
    '''
    Tweak sleep globally by multple, a fraction, or depend on env
    '''
    from time import sleep
    sleep(float)

class SeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTest, cls).setUpClass()

        # Override the email backend so that we can capture sent emails.
        from django.conf import settings
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        # Override ALLOWED_HOSTS, SITE_ROOT_URL, and ORGANIZATION_PARENT_DOMAIN
        # because they may not be set or set properly in the local environment's
        # non-test settings for the URL assigned by the LiveServerTestCase server.
        settings.ALLOWED_HOSTS = ['.localhost']
        settings.SITE_ROOT_URL = cls.live_server_url
        settings.ORGANIZATION_PARENT_DOMAIN = 'orgs.localhost'

        ## Turn on DEBUG so we can see errors better.
        #settings.DEBUG = True

        # Start a headless browser.
        import selenium.webdriver
        import os
        os.environ['PATH'] += ":/usr/lib/chromium-browser" # 'chromedriver' executable needs to be in PATH
        cls.browser = selenium.webdriver.Chrome()
        cls.browser.implicitly_wait(3) # seconds

    @classmethod
    def tearDownClass(cls):
        # Terminate the selenium browser.
        cls.browser.quit()

        # Run superclass termination.
        super(SeleniumTest, cls).tearDownClass()

    def setUp(self):
        # clear the browser's cookies before each test
        self.browser.delete_all_cookies()

    def url(self, subdomain, path):
        # Construct a URL to the desired page. Use self.live_server_url
        # (set by StaticLiveServerTestCase) to determine the scheme, hostname,
        # and port the test server is running on. Add the subdomain (if not None)
        # and path.
        import urllib.parse
        s = urllib.parse.urlsplit(self.live_server_url)
        scheme, host = (s[0], s[1])
        if subdomain:
            port = '' if (':' not in host) else (':'+host.split(':')[1])
            host = subdomain + '.' + settings.ORGANIZATION_PARENT_DOMAIN + port
        base_url = urllib.parse.urlunsplit((scheme, host, '', '', ''))
        return urllib.parse.urljoin(base_url, path)

    def fill_field(self, css_selector, text):
        self.browser.find_element_by_css_selector(css_selector).send_keys(text)

    def click_element(self, css_selector):
        self.browser.find_element_by_css_selector(css_selector).click()

    def select_option(self, css_selector, value):
        from selenium.webdriver.support.select import Select
        e = self.browser.find_element_by_css_selector(css_selector)
        Select(e).select_by_value(value)

    def _getNodeText(self, css_selector):
        node_text = self.browser.find_element_by_css_selector(css_selector).text
        node_text = re.sub(r"\s+", " ", node_text) # normalize whitespace
        return node_text

    def assertInNodeText(self, search_text, css_selector):
        self.assertIn(search_text, self._getNodeText(css_selector))
    def assertNotInNodeText(self, search_text, css_selector):
        self.assertNotIn(search_text, self._getNodeText(css_selector))

    def assertNodeNotVisible(self, css_selector):
        from selenium.common.exceptions import NoSuchElementException
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector(css_selector)

    def pop_email(self):
        self.assertTrue(self.has_more_email())
        import django.core.mail
        return django.core.mail.outbox.pop(0)

    def has_more_email(self):
        import django.core.mail
        try:
            # The outbox attribute doesn't exist until the first
            # message is sent.
            return len(django.core.mail.outbox) > 0
        except AttributeError:
            return False

#####################################################################

class LandingSiteFunctionalTests(SeleniumTest):
    def url(self, path):
        # Within this test, we only generate URLs for the landing site.
        return super().url(None, path)

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "GovReady Q")

class OrganizationSiteFunctionalTests(SeleniumTest):

    def setUp(self):
        super().setUp()

        # Load the Q modules from the fixtures directory.
        # The account settings project and its one submodule are required
        # in order to run the system.
        settings.MODULES_PATH = 'fixtures/modules'
        from guidedmodules.management.commands.load_modules import Command as load_modules
        load_modules().handle()

        # Create the Organization.
        from siteapp.models import Organization
        org = Organization.objects.create(name="Our Organization", subdomain="testorg")

        # Create a default user that is a member of the organization.
        from siteapp.models import User, ProjectMembership
        self.user = User.objects.create(username="me")
        self.user.set_password("1234")
        self.user.save()
        ProjectMembership.objects.get_or_create(user=self.user, project=org.get_organization_project())

        # And initialize the root Task of the Organization with this user as its editor.
        org.get_organization_project().set_root_task("organization", self.user)

    def url(self, path):
        # Within this test, we only generate URLs for the organization subdomain.
        return super().url("testorg", path)

    def _login(self):
        # Fill in the login form and submit.
        self.browser.get(self.url("/"))

        self.assertRegex(self.browser.title, "Home")
        self.fill_field("#id_login", "me")
        self.fill_field("#id_password", "1234")
        self.click_element("form button.primaryAction")

    def _new_project(self):
        self.browser.get(self.url("/projects"))
        self.click_element("#new-project")
        self.fill_field("#id_title", "My Simple Project")
        self.click_element("#id_module_id_0")
        self.click_element("button[type=submit]")
        var_sleep(1)
        self.assertRegex(self.browser.title, "My Simple Project")

    def _start_task(self):
        # Assumes _new_project() just finished.

        # Start the task.
        self.click_element('#question-simple_module .task-commands form.start-task a')

    def _accept_invitation(self, email):
        # Assumes an invitation email was sent.

        import random

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

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "GovReady Q")

    def test_login(self):
        # Log in as a new user, log out, then log in a second time.
        # We should only get the account settings questions on the
        # first login.
        self._login()
        self.browser.get(self.url("/accounts/logout/"))
        self._login()

    def test_new_user_account_settings(self):
        # Log in as the user, who is new. Complete the account settings.

        self._login()

        self.click_element('#please-complete-account-settings a')
        var_sleep(.5) # wait for page to load
        self.assertIn("Introduction | GovReady Account Settings", self.browser.title)

        # - The user is looking at the Introduction page.
        self.click_element("#save-button")
        var_sleep(.5) # wait for page to load

        # - Now at the what is your name page?
        self.fill_field("#inputctrl", "John Doe")
        self.click_element("#save-button")
        var_sleep(.5) # wait for page to load

        # - We're on the module finished page.
        self.assertNodeNotVisible('#return-to-project')
        self.click_element("#return-to-projects")
        var_sleep(1.5)
        self.assertRegex(self.browser.title, "Home")
        self.assertNodeNotVisible('#please-complete-account-settings')

    def test_simple_module(self):
        # Log in and create a new project and start its task.
        self._login()
        self._new_project()
        self._start_task()

        # Answer the questions.

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # Text question.
        self.assertRegex(self.browser.title, "Next Question: The Question")
        self.fill_field("#inputctrl", "This is some text.")
        self.click_element("#save-button")
        var_sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^A Simple Module - ")

    def test_invitations(self):
        # Test a bunch of invitations.

        # Log in and create a new project.
        self._login()
        self._new_project()
        project_page = self.browser.current_url

        # And create a new task.
        self._start_task()
        task_page = self.browser.current_url

        # But now go back to the project page.
        self.browser.get(project_page)

        def do_invitation(email):
            # Fill out the invitation modal.
            var_sleep(.5) # wait for modal to show

            # in case there are other team members and the select box is showing,
            # choose
            self.select_option('#invite-user-select', '__invite__')

            self.fill_field("#invitation_modal #invite-user-email", email)
            self.click_element("#invitation_modal button.btn-submit")
            var_sleep(1) # wait for invitation to be sent

            # Log out and accept the invitation as an anonymous user.
            self.browser.get(self.url("/accounts/logout/"))
            self._accept_invitation(email)

        def reset_login():
            # Log out and back in as the original user.
            self.browser.get(self.url("/accounts/logout/"))
            self._login()
            self.browser.get(project_page)
            var_sleep(1)

        # Test an invitation to that project.
        self.click_element("#show-project-settings")
        var_sleep(.5) # modal fades in
        self.click_element("#invite-user-to-project")
        do_invitation("test+project@q.govready.com")
        self.assertRegex(self.browser.title, "My Simple Project") # user is on the project page
        self.click_element('#question-simple_module .started-task a') # go to the task page
        self.assertRegex(self.browser.title, "A Simple Module") # user is on the task page
        self.assertInNodeText("is editing this module. You cannot make changes to it.", "#auth-status .text-danger")

        reset_login()

        # Test an invitation to take over editing a task but without joining the project.
        self.click_element('#question-simple_module .started-task a') # go to the task page
        var_sleep(.5) # wait for page to load
        self.click_element("#save-button") # pass over the Introductory question because the Help link is suppressed on interstitials
        var_sleep(.5) # wait for page to load
        self.click_element('#transfer-editorship a')
        do_invitation("test+editor@q.govready.com")
        var_sleep(5)
        self.assertRegex(self.browser.title, "A Simple Module") # user is on the task page
        self.assertNodeNotVisible("#auth-status .text-danger")

        reset_login()

        # Test an invitation for a user to begin a new task within a Project.
        self.click_element('#question-simple_module_two .task-commands a.assign-task')
        do_invitation("test+begintask@q.govready.com")
        self.assertRegex(self.browser.title, "A Simple Module") # user is on the task page
        self.assertNodeNotVisible("#auth-status .text-danger")

        # Invitations to join discussions are tested in test_discussion.

    def test_discussion(self):
        from siteapp.management.commands.send_notification_emails import Command as send_notification_emails

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
        var_sleep(.5) # wait for options to slideDown
        self.click_element("#discussion .comment-input button.btn-primary")

        # Invite a guest to join.
        var_sleep(.5) # wait for the you-are-alone div to show
        self.click_element("#discussion-you-are-alone a")
        var_sleep(.5) # wait for modal to show
        self.fill_field("#invitation_modal #invite-user-email", "invited-user@q.govready.com")
        self.click_element("#invitation_modal button.btn-submit")
        var_sleep(1) # wait for invitation to be sent

        # Now we become that guest. Log out.
        # Then accept the invitation as an anonymous user.
        self.browser.get(self.url("/accounts/logout/"))
        self._accept_invitation("test+account@q.govready.com")
        var_sleep(1) # wait for the invitation to be accepted

        # Check that the original user received a notification that the invited user
        # accepted the invitation.
        send_notification_emails().send_new_emails()
        self.assertRegex(self.pop_email().body, "accepted your invitation to join the discussion")

        # This takes the user directly to the discussion they were invited to join.
        # Leave a comment.
        self.fill_field("#discussion-your-comment", "Yes, @me, I am here!\n\nI am here with you!")
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(.5) # wait for it to submit

        # Test that a notification was sent to the main user.
        from notifications.models import Notification
        self.assertTrue(Notification.objects.filter(
            recipient=self.user,
            verb="mentioned you in a comment on").exists())

        # Test that the notification is emailed out to the main user.
        send_notification_emails().send_new_emails()
        notification_email_body = self.pop_email().body
        self.assertRegex(notification_email_body, "mentioned you in")

        # Leave an emoji reaction on the initial user's comment.
        self.click_element(".react-with-emoji")
        var_sleep(.5) # emoji selector shows
        self.click_element("#emoji-selector .emoji[data-emoji-name=heart]") # makes active
        self.click_element("body") # closes emoji panel and submits via ajax
        var_sleep(.5) # emoji reaction submitted

        var_sleep(5)

        # Log back in as the original user.
        discussion_page = self.browser.current_url
        self.browser.get(self.url("/accounts/logout/"))
        self._login()
        self.browser.get(discussion_page)

        # Test that we can see the comment and the reaction.
        self.assertInNodeText("Yes, @me, I am here", "#discussion .comment:not(.author-is-self) .comment-text")
        self.assertInNodeText("reacted", "#discussion .replies .reply[data-emojis=heart]")

    def test_questions_text(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_text .task-commands form.start-task a')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # text
        self.assertRegex(self.browser.title, "Next Question: text")
        self.fill_field("#inputctrl", "This is some text.")
        self.click_element("#save-button")
        var_sleep(.5)

        # password
        self.assertRegex(self.browser.title, "Next Question: password")
        self.fill_field("#inputctrl", "th1s1z@p@ssw0rd!")
        self.click_element("#save-button")
        var_sleep(.5)

        # email-address
        import random
        self.assertRegex(self.browser.title, "Next Question: email-address")
        self.fill_field("#inputctrl", "test+%d@q.govready.com" % random.randint(10000, 99999))
        self.click_element("#save-button")
        var_sleep(.5)

        # url
        self.assertRegex(self.browser.title, "Next Question: url")
        self.fill_field("#inputctrl", "https://q.govready.com")
        self.click_element("#save-button")
        var_sleep(.5)

        # longtext
        self.assertRegex(self.browser.title, "Next Question: longtext")
        self.fill_field("#inputctrl", "This is a paragraph.\n\nThis is another paragraph.")
        self.click_element("#save-button")
        var_sleep(.5)

        # date
        self.assertRegex(self.browser.title, "Next Question: date")
        self.select_option("select[name='value_year']", "2016")
        self.select_option("select[name='value_month']", "8")
        self.select_option("select[name='value_day']", "22")
        self.click_element("#save-button")
        var_sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Text Input Question Types - ")

    def test_questions_choice(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_choice .task-commands form.start-task a')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # choice
        self.assertRegex(self.browser.title, "Next Question: choice")
        self.click_element('#question input[name="value"][value="choice2"]')
        self.click_element("#save-button")
        var_sleep(.5)

        # yesno
        self.assertRegex(self.browser.title, "Next Question: yesno")
        self.click_element('#question input[name="value"][value="yes"]')
        self.click_element("#save-button")
        var_sleep(.5)

        # multiple-choice
        self.assertRegex(self.browser.title, "Next Question: multiple-choice")
        self.click_element('#question input[name="value"][value="choice1"]')
        self.click_element('#question input[name="value"][value="choice3"]')
        self.click_element("#save-button")
        var_sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Choice Question Types - ")

    def test_questions_numeric(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_numeric .task-commands form.start-task a')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # integer
        self.assertRegex(self.browser.title, "Next Question: integer")
        self.fill_field("#inputctrl", "5000")
        self.click_element("#save-button")
        var_sleep(.5)

        # real
        self.assertRegex(self.browser.title, "Next Question: real")
        self.fill_field("#inputctrl", "0.050")
        self.click_element("#save-button")
        var_sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Numeric Question Types - ")
    
    def test_questions_media(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_media .task-commands form.start-task a')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # file
        # TODO: Test an actual file upload. For now we're just skipping
        # the question.
        self.assertRegex(self.browser.title, "Next Question: file")
        self.click_element("#skip-button")
        var_sleep(.5)

        # interstitial
        # nothing to really test in terms of functionality, but we could check that
        # page elements are present
        self.assertRegex(self.browser.title, "Next Question: interstitial")
        self.click_element("#save-button")
        var_sleep(.5)

        # external-function
        # There is nothing to really test in terms of functionality here, but
        # the template result should show the output of the sample_external_function
        # method defined below.
        self.assertRegex(self.browser.title, "Next Question: external-function")
        self.click_element("#save-button")
        var_sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Media Question Types - ")

    def test_questions_module(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_module .task-commands form.start-task a')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # "You will now begin a module."
        self.assertRegex(self.browser.title, "Next Question: module")
        self.click_element("#save-button")
        var_sleep(.5)

        # We're now at the intro screen for the simple sub-module.
        # Grab the page URL here so we can figure out the ID of this task
        # so that we can select it again later.
        import urllib.parse
        s = urllib.parse.urlsplit(self.browser.current_url)
        m = re.match(r"/tasks/(\d+)/a-simple-module", s[2])
        task_id = int(m.group(1))

        def do_submodule(answer_text):
            self.assertRegex(self.browser.title, "Next Question: Introduction")
            self.click_element("#save-button")
            var_sleep(.5)
            self.assertRegex(self.browser.title, "Next Question: The Question")
            self.fill_field("#inputctrl", answer_text)
            self.click_element("#save-button")
            var_sleep(.5)
            self.assertRegex(self.browser.title, "^A Simple Module - ")

            # Return to the main module.
            self.click_element("#return-to-supertask")
            var_sleep(.5)

        do_submodule("My first answer.")
        self.assertRegex(self.browser.title, "^Test The Module Question Types - ")

        # Go back to the question and start a second answer.
        def change_answer():
            self.click_element("#link-to-question-q_module a")
            var_sleep(.5)
        change_answer()
        self.assertRegex(self.browser.title, "Next Question: module")
        self.click_element('#question input[name="value"][value="__new"]')
        self.click_element("#save-button")
        var_sleep(.5)
        do_submodule("My second answer.")
        self.assertRegex(self.browser.title, "^Test The Module Question Types - ")

        # Go back and change the answer to the first one again.
        change_answer()
        self.assertRegex(self.browser.title, "Next Question: module")
        self.click_element('#question input[name="value"][value="%d"]' % task_id)
        self.click_element("#save-button")
        var_sleep(.5)
        self.assertRegex(self.browser.title, "^Test The Module Question Types - ")

    def test_questions_encrypted(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_encrypted .task-commands form.start-task a')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # text
        self.assertRegex(self.browser.title, "Next Question: text with encryption")
        self.fill_field("#inputctrl", "This is some text that will be encrypted in our database.")
        self.click_element("#save-button")
        var_sleep(.5)

        # We're now in the output page and we can see if we can still see
        # the answer.
        self.assertInNodeText('some text that will be encrypted', '#document-1-body')

        # Clear the cookie that holds the encrpytion key, reload the page,
        # and see that the value disappears.
        self.browser.delete_cookie("encr_eph_1");
        self.browser.get(self.browser.current_url)
        var_sleep(.5)
        self.assertNotInNodeText('some text that will be encrypted', '#document-1-body')

def sample_external_function(question, answers, **kwargs):
    # For test_questions_media's module.
    return repr((question, answers))