# This module defines a SeleniumTest class that is used here and in
# the discussion app to run Selenium and Chrome-based functional/integration
# testing.
#
# Selenium requires that 'chromedriver' be on the system PATH. The
# Ubuntu package chromium-chromedriver installs Chromium and
# chromedriver. But if you also have Google Chrome installed, it
# picks up Google Chrome which might be of an incompatible version.
# So we hard-code the Chromium binary using options.binary_location="/usr/bin/chromium-browser".
# If paths differ on your system, you may need to set the PATH system
# environment variable and the options.binary_location field below.

import os
import os.path
import pathlib
import re
import tempfile
import selenium.webdriver
from django.contrib.auth.models import Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# StaticLiveServerTestCase can server static files but you have to make sure settings have DEBUG set to True
from django.utils.crypto import get_random_string

from siteapp.models import (Organization, Portfolio, Project,
                            ProjectMembership, User)
from siteapp.settings import HEADLESS, DOS
from tools.utils.linux_to_dos import convert_w


def var_sleep(duration):
    '''
    Tweak sleep globally by multple, a fraction, or depend on env
    '''
    from time import sleep
    sleep(duration*2)

class SeleniumTest(StaticLiveServerTestCase):
    window_geometry = (1200, 1200)

    @classmethod
    def setUpClass(cls):
        super(SeleniumTest, cls).setUpClass()

        # Override the email backend so that we can capture sent emails.
        from django.conf import settings
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        # Override ALLOWED_HOSTS, SITE_ROOT_URL, etc.
        # because they may not be set or set properly in the local environment's
        # non-test settings for the URL assigned by the LiveServerTestCase server.
        # StaticLiveServerTestCase can server static files but you have to make sure settings have DEBUG set to True
        settings.ALLOWED_HOSTS = ['localhost', 'testserver']
        settings.SITE_ROOT_URL = cls.live_server_url
        settings.DEBUG = True

        # In order for these tests to succeed when not connected to the
        # Internet, disable email deliverability checks which query DNS.
        settings.VALIDATE_EMAIL_DELIVERABILITY = False

        ## Turn on DEBUG so we can see errors better.
        #settings.DEBUG = True

        # Start a headless browser.

        options = selenium.webdriver.ChromeOptions()
        options.add_argument("disable-infobars") # "Chrome is being controlled by automated test software."
        if SeleniumTest.window_geometry == "maximized":
            options.add_argument("start-maximized") # too small screens make clicking some things difficult
        else:
            options.add_argument("--window-size=" + ",".join(str(dim) for dim in SeleniumTest.window_geometry))

        options.add_argument("--incognito")

        if DOS:
            # WSL has a hard time finding tempdir so we feed it the dos conversion
            tempfile.tempdir = convert_w(os.getcwd())
        # enable Selenium support for downloads
        cls.download_path = pathlib.Path(tempfile.gettempdir())
        options.add_experimental_option("prefs", {
            "download.default_directory": str(cls.download_path),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        if HEADLESS:
            options.add_argument('--headless')

        # Set up selenium Chrome browser for Windows or Linux
        if DOS:
            # TODO: Find out a way to get chromedriver implicit executable path in WSL
            cls.browser = selenium.webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        else:
            cls.browser = selenium.webdriver.Chrome(chrome_options=options)

        cls.browser.implicitly_wait(3) # seconds

        # Clean up and quit tests if Q is in SSO mode
        if getattr(settings, 'PROXY_HEADER_AUTHENTICATION_HEADERS', None):
            print("Cannot run tests.")
            print("Tests will not run when IAM Proxy enabled (e.g., when `local/environment.json` sets `trust-user-authentication-headers` parameter.)")
            cls.browser.quit()
            super(SeleniumTest, cls).tearDownClass()
            exit()

    @classmethod
    def tearDownClass(cls):
        # Terminate the selenium browser.
        cls.browser.quit()

        # Run superclass termination.
        super(SeleniumTest, cls).tearDownClass()

    def setUp(self):
        # clear the browser's cookies before each test
        self.browser.delete_all_cookies()

    def navigateToPage(self, path):
        self.browser.get(self.url(path))

    def url(self, path):
        # Construct a URL to the desired page. Use self.live_server_url
        # (set by StaticLiveServerTestCase) to determine the scheme, hostname,
        # and port the test server is running on. Add the path.
        import urllib.parse
        return urllib.parse.urljoin(self.live_server_url, path)

    def clear_field(self, css_selector):
        self.browser.find_element_by_css_selector(css_selector).clear()

    def fill_field(self, css_selector, text):
        self.browser.find_element_by_css_selector(css_selector).send_keys(text)

    def clear_and_fill_field(self, css_selector, text):
        self.clear_field(css_selector)
        self.fill_field(css_selector, text)

    def click_element_with_link_text(self, text):
        elem = self.browser.find_elements_by_link_text(text)
        elem[0].click()

    def click_element_with_xpath(self, xpath):
        elem = self.browser.find_elements_by_xpath(xpath)
        elem[0].click()

    def click_element(self, css_selector):
        # ensure element is on screen or else it can't be clicked
        # see https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView
        elem = self.browser.find_element_by_css_selector(css_selector)
        self.browser.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });", elem)
        elem.click()
        
    def find_selected_option(self, css_selector):
        selected_option = self.browser.find_element_by_css_selector(f"{css_selector}")
        return selected_option

    def select_option(self, css_selector, value):
        from selenium.webdriver.support.select import Select
        e = self.browser.find_element_by_css_selector(css_selector)
        Select(e).select_by_value(value)

    def select_option_by_visible_text(self, css_selector, text):
        from selenium.webdriver.support.select import Select
        e = self.browser.find_element_by_css_selector(css_selector)
        Select(e).select_by_visible_text(text)

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
        # The outbox attribute doesn't exist until the backend
        # instance is initialized when the first message is sent.
        outbox = getattr(django.core.mail, 'outbox', [])
        return len(outbox) > 0

    def filepath_conversion(self, file_input, filepath, conversion_type):
        if conversion_type.lower() == "sendkeys":
            try:
                # Current file system path might be incongruent linux-dos
                file_input.send_keys(filepath)
            except Exception as ex:
                print("Changing file path from linux to dos")
                print(ex)
                filepath = convert_w(filepath)
                file_input.send_keys(filepath)
        elif conversion_type.lower() == "fill":
            try:
                # Current file system path might be incongruent linux-dos
                self.fill_field(file_input, filepath)
            except Exception as ex:
                print("Changing file path from linux to dos")
                print(ex)
                filepath = convert_w(filepath)
                self.fill_field(file_input, filepath)
        return filepath

#####################################################################

class SupportPageTests(SeleniumTest):
    def test_supportpage(self):
        self.browser.get(self.url("/support"))
        self.assertRegex(self.browser.title, "Support")

    def test_supportpage_customize(self):
        self.browser.get(self.url("/support"))
        self.assertRegex(self.browser.title, "Support")
        self.assertInNodeText("This page has not be set up.", "#support_content")

        # Update content
        from siteapp.models import Support
        support = Support()
        support.text = "Updated support text."
        support.email = "support@govready.com"
        support.url = "https://govready.com/support"
        support.phone = "212-555-5555"
        support.save()
        self.browser.get(self.url("/support"))
        self.assertInNodeText("Updated support text.", "#support_content")
        self.assertInNodeText("support@govready.com", "#support_content")

class LandingSiteFunctionalTests(SeleniumTest):
    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")

class OrganizationSiteFunctionalTests(SeleniumTest):

    def setUp(self):
        super().setUp()

        # Load the Q modules from the fixtures directory.
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
            spec={ # contains a test project
                "type": "local",
                "path": "fixtures/modules/other",
            },
            trust_assets=True
        )\
            .add_app_to_catalog("simple_project")

        # Create a default user that is a member of the organization.
        # Log the user into the test client, which is used for API
        # tests. The Selenium tests require a separate log in via the
        # headless browser.

        # self.user = User.objects.create_superuser(
        self.user = User.objects.create(
            username="me",
            email="test+user@q.govready.com",
            is_staff=True
        )
        self.user.clear_password = get_random_string(16)
        self.user.set_password(self.user.clear_password)
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.user.save()
        self.user.reset_api_keys()
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.client.login(username=self.user.username, password=self.user.clear_password)

        # Create a Portfolio and Grant Access
        portfolio = Portfolio.objects.create(title=self.user.username)
        portfolio.assign_owner_permissions(self.user)

        # Create the Organization.
        self.org = Organization.create(name="Our Organization", slug="testorg",
            admin_user=self.user)

        # Grant the user permission to change the review state of answers.
        self.org.reviewers.add(self.user)

        # create a second user
        self.user2 = User.objects.create(
            username="me2",
            email="test+user2@q.govready.com")
        self.user2.clear_password = get_random_string(16)
        self.user2.set_password(self.user2.clear_password)
        self.user2.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.user2.save()
        self.user2.reset_api_keys()
        self.user2.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.client.login(username=self.user2.username, password=self.user2.clear_password)
        portfolio = Portfolio.objects.create(title=self.user2.username)
        portfolio.assign_owner_permissions(self.user2)

        # create a third user
        self.user3 = User.objects.create(
            username="me3",
            email="test+user3@q.govready.com")
        self.user3.clear_password = get_random_string(16)
        self.user3.set_password(self.user3.clear_password)
        self.user3.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.user3.save()
        self.user3.reset_api_keys()
        self.user3.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.client.login(username=self.user3.username, password=self.user3.clear_password)
        portfolio = Portfolio.objects.create(title=self.user3.username)
        portfolio.assign_owner_permissions(self.user3)

        # Grant second user membership in the organization
        # from https://github.com/GovReady/govready-q/blob/master/siteapp/admin.py#L41
        mb, isnew = ProjectMembership.objects.get_or_create(
            user=self.user2,
            project=self.org.get_organization_project(),
            )

    def client_get(self, *args, **kwargs):
        resp = self.client.get(
            *args,
            **kwargs)
        self.assertEqual(resp.status_code, 200, msg=repr(resp))
        return resp # .content.decode("utf8")

    def _login(self, username=None, password=None):
        # Fill in the login form and submit. Use self.user's credentials
        # unless they are overridden in the arguments to test failed logins
        # with other credentials.
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")
        self.click_element("li#tab-signin")
        self.fill_field("#id_login", username or self.user.username)
        self.fill_field("#id_password", password or self.user.clear_password)
        self.click_element("form#login_form button[type=submit]")

    def _new_project(self):
        self.browser.get(self.url("/projects"))
        self.click_element("#new-project")

        # Select Portfolio
        self.select_option_by_visible_text('#id_portfolio', self.user.username)
        self.click_element("#select_portfolio_submit")
        # TODO add permissions to the user to see certain things by role and individuals
        #
        var_sleep(2)

        # Click Add Button
        self.click_element(".app[data-app='project/simple_project'] .start-app")

        var_sleep(2)
        self.assertRegex(self.browser.title, "I want to answer some questions on Q.")

        m = re.match(r"http://.*?/projects/(\d+)/", self.browser.current_url)
        self.current_project = Project.objects.get(id=m.group(1))

    def _start_task(self):
        # Assumes _new_project() just finished.

        # Start the task.
        var_sleep(0.4)
        self.click_element('#question-simple_module')

        # Return the Task instance that we just created or are now visiting.
        from guidedmodules.models import Task
        return Task.objects.get(id=re.search(r"/tasks/(\d+)/", self.browser.current_url).group(1))

class GeneralTests(OrganizationSiteFunctionalTests):

    def _accept_invitation(self, username):
        # Assumes an invitation email was sent.

        # Extract the URL in the email and visit it.
        invitation_body = self.pop_email().body
        invitation_url_pattern = re.escape(self.url("/invitation/")) + r"\S+"
        print("invitation_url_pattern", invitation_url_pattern)
        self.assertRegex(invitation_body, invitation_url_pattern)
        m = re.search(invitation_url_pattern, invitation_body)
        print("m.group(0)", m.group(0))
        self.browser.get(m.group(0))
        var_sleep(0.5) # wait for page to load
        # Since we're not logged in, we hit the invitation splash page.
        self.click_element('#button-sign-in')
        print("###################################")
        var_sleep(0.5) # wait for page to load
        self.assertRegex(self.browser.title, "Sign In")

        # TODO check if the below should still be happening
        # Test that an allauth confirmation email was sent.
        # self.assertIn("Please confirm your email address at GovReady Q by following this link", self.pop_email().body)

    def _fill_in_signup_form(self, email, username=None):
        if username:
            self.fill_field("#id_username", username)
        else:
            self.fill_field("#id_username", "test+%s@q.govready.com" % get_random_string(8))
        self.fill_field("#id_email", email)
        new_test_user_password = get_random_string(16)
        self.fill_field("#id_password1", new_test_user_password)
        self.fill_field("#id_password2", new_test_user_password)

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")

    def test_login(self):
        # Test that a wrong pwd doesn't log us in.
        self._login(password=get_random_string(4))
        self.assertInNodeText("The username and/or password you specified are not correct.", "form#login_form .alert-danger")

        # Test that a wrong username doesn't log us in.
        self._login(username="notme")
        self.assertInNodeText("The username and/or password you specified are not correct.", "form#login_form .alert-danger")

        # Log in as a new user, log out, then log in a second time.
        # We should only get the account settings questions on the
        # first login.
        self._login()
        self.browser.get(self.url("/accounts/logout/"))
        self._login()

    def test_new_user_account_settings(self):
        # Log in as the user, who is new. Complete the account settings.

        self._login()

        self.click_element('#user-menu-dropdown')
        var_sleep(0.75) # wait for menu to open

        self.click_element('#user-menu-account-settings')
        var_sleep(1) # wait for page to open
        self.assertIn("Introduction | GovReady Account Settings", self.browser.title)

        # - The user is looking at the Introduction page.
        self.click_element("#save-button")
        var_sleep(1.0) # wait for page to load

        # - Now at the what is your name page?
        self.fill_field("#inputctrl", "John Doe")
        self.click_element("#save-button")
        var_sleep(.5) # wait for page to load

        # - We're on the module finished page.
        self.assertNodeNotVisible('#return-to-project')
        self.click_element("#return-to-projects")
        var_sleep(1.5)
        self.assertRegex(self.browser.title, "Your Compliance Projects")
        self.assertNodeNotVisible('#please-complete-account-settings')

    def test_static_pages(self):
        self.browser.get(self.url("/privacy"))
        self.assertRegex(self.browser.title, "Privacy Policy")
        var_sleep(0.5)
        self.browser.get(self.url("/terms-of-service"))
        self.assertRegex(self.browser.title, "Terms of Service")
        var_sleep(0.5)
        self.browser.get(self.url("/love-assessments"))
        self.assertRegex(self.browser.title, "Love Assessments")
        var_sleep(0.5)

    def test_simple_module(self):
        # Log in and create a new project and start its task.
        self._login()
        self._new_project()
        task = self._start_task()

        # Answer the questions.

        # Introduction screen.
        var_sleep(1)
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(1.75)

        # Text question.
        self.assertIn("| A Simple Module - GovReady-Q", self.browser.title)
        self.fill_field("#inputctrl", "This is some text.")
        self.click_element("#save-button")
        var_sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^A Simple Module - ")

        # Go to project page, then review page.
        # self.click_element("#return-to-project")
        self.click_element("#review-answers")

        # Mark the answer as reviewed then test that it was saved.
        var_sleep(2)
        self.click_element(".task-" + str(task.id) + "-answer-q1-review-1")
        var_sleep(2) # wait for ajax
        for question, answer in task.get_current_answer_records():
            if question.key == "q1":
                self.assertEqual(answer.reviewed, 1)

    def test_invitations(self):
        print("INFO: Entering '{}'".format('test_invitations(self)'))
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

        def start_invitation(username):
            print("INFO: Entering '{}', '{}'".format('start_invitation(username)', username))
            # Fill out the invitation modal.
            # self.select_option_by_visible_text('#invite-user-select', username) # This is for selecting user from dropdown list
            var_sleep(1)
            self.fill_field("input#invite-user-email", username)
            var_sleep(1)
            self.click_element("#invitation_modal button.btn-submit")

        def do_invitation(username):
            print("INFO: Entering '{}', '{}'".format('do_invitation(username)', username))
            start_invitation(username)
            var_sleep(1) # wait for invitation to be sent

            # Log out and accept the invitation as an anonymous user.
            self.browser.get(self.url("/accounts/logout/"))
            self._accept_invitation(username)

        def reset_login():
            print("INFO: Entering '{}'".format('reset_login()'))
            # Log out and back in as the original user.
            self.browser.get(self.url("/accounts/logout/"))
            self._login()
            self.browser.get(project_page)
            var_sleep(1)

        # Test an invitation to that project. For unknown reasons, when
        # executing this on CircleCI (but not locally), the click fails
        # because the element is not clickable -- it reports a coordinate
        # that's above the button in the site header. Not sure what's
        # happening. So load the modal using Javascript.
        self.click_element("#show-project-invite")
        self.browser.execute_script("invite_user_into_project()")
        # Toggle field to invite user by email
        self.browser.execute_script("$('#invite-user-email').parent().toggle(true)")

        # Test an invalid email address.
        start_invitation("example")
        var_sleep(.5)
        self.assertInNodeText("The email address is not valid.", "#global_modal") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.25)
        self.click_element("#show-project-invite") # Re-open the invite box.
        self.browser.execute_script("invite_user_into_project()") # See comment above.
        # Toggle field to invite user by email
        self.browser.execute_script("$('#invite-user-email').parent().toggle(true)")

        do_invitation(self.user2.email)
        self.fill_field("#id_login", self.user2.username)
        self.fill_field("#id_password", self.user2.clear_password)
        self.click_element("form button.primaryAction")

        self.assertRegex(self.browser.title, "I want to answer some questions on Q") # user is on the project page
        var_sleep(1.5)
        self.click_element('#question-simple_module') # go to the task page
        var_sleep(1.5)
        self.assertRegex(self.browser.title, "Next Question: Introduction") # user is on the task page

        # reset_login()

        # Test an invitation to take over editing a task but without joining the project.
        var_sleep(2)

        self.click_element("#save-button") # pass over the Introductory question because the Help link is suppressed on interstitials
        self.click_element('#transfer-editorship')
        # Toggle field to invite user by email
        self.browser.execute_script("$('#invite-user-email').parent().toggle(true)")
        var_sleep(2)
        do_invitation(self.user3.email)
        self.fill_field("#id_login", self.user3.username)
        self.fill_field("#id_password", self.user3.clear_password)
        self.click_element("form button.primaryAction")
        var_sleep(1.5)
        self.assertRegex(self.browser.title, "Next Question: The Question") # user is on the task page

        # Test assigning existing user to a project.
        reset_login()
        self._new_project()
        project_page = self.browser.current_url

        # And create a new task.
        self._start_task()
        task_page = self.browser.current_url

        # But now go back to the project page.
        self.browser.get(project_page)
        var_sleep(1.25)
        self.click_element("#show-project-invite")
        var_sleep(0.75)
        # Select username "me3"
        self.select_option_by_visible_text('#invite-user-select', "me3")
        self.click_element("#invite_submit_btn")
        var_sleep(0.75)
        self.assertTrue("× me3 granted edit permission to project." == self._getNodeText(".alert-info"))
       
        # reset_login()

        # Invitations to join discussions are tested in test_discussion.

    # def test_discussion(self):
        # from siteapp.management.commands.send_notification_emails import Command as send_notification_emails

        # # Log in and create a new project.
        # self._login()
        # self._new_project()
        # self._start_task()

        # # Move past the introduction screen.
        # self.assertRegex(self.browser.title, "Next Question: Introduction")
        # self.click_element("#save-button")
        # var_sleep(.8) # wait for page to reload

        # # We're now on the first actual question.
        # # Start a team conversation.
        # self.click_element("#start-a-discussion")
        # self.fill_field("#discussion-your-comment", "Hello is anyone *here*?")
        # var_sleep(.5) # wait for options to slideDown
        # self.click_element("#discussion .comment-input button.btn-primary")

        # # Invite a guest to join.
        # var_sleep(.5) # wait for the you-are-alone div to show
        # self.click_element("#discussion-you-are-alone a")
        # self.fill_field("#invitation_modal #invite-user-email", "invited-user@q.govready.com")
        # self.click_element("#invitation_modal button.btn-submit")
        # var_sleep(1) # wait for invitation to be sent

        # # Now we become that guest. Log out.
        # # Then accept the invitation as an anonymous user.
        # self.browser.get(self.url("/accounts/logout/"))
        # self._accept_invitation("test+account@q.govready.com")
        # var_sleep(1) # wait for the invitation to be accepted

        # # Check that the original user received a notification that the invited user
        # # accepted the invitation.
        # send_notification_emails().send_new_emails()
        # self.assertRegex(self.pop_email().body, "accepted your invitation to join the discussion")

        # # This takes the user directly to the discussion they were invited to join.
        # # Leave a comment.

        # self.fill_field("#discussion-your-comment", "Yes, @me, I am here!\n\nI am here with you!")
        # self.click_element("#discussion .comment-input button.btn-primary")
        # var_sleep(.5) # wait for it to submit

        # # Test that a notification was sent to the main user.
        # from notifications.models import Notification
        # self.assertTrue(Notification.objects.filter(
        #     recipient=self.user,
        #     verb="mentioned you in a comment on").exists())

        # # Test that the notification is emailed out to the main user.
        # send_notification_emails().send_new_emails()
        # notification_email_body = self.pop_email().body
        # self.assertRegex(notification_email_body, "mentioned you in")

        # # Leave an emoji reaction on the initial user's comment.
        # self.click_element(".react-with-emoji")
        # var_sleep(.5) # emoji selector shows
        # self.click_element("#emoji-selector .emoji[data-emoji-name=heart]") # makes active
        # self.click_element("body") # closes emoji panel and submits via ajax
        # var_sleep(.5) # emoji reaction submitted

        # # Log back in as the original user.
        # discussion_page = self.browser.current_url
        # self.browser.get(self.url("/accounts/logout/"))
        # self._login()
        # self.browser.get(discussion_page)

        # # Test that we can see the comment and the reaction.
        # self.assertInNodeText("Yes, @me, I am here", "#discussion .comment:not(.author-is-self) .comment-text")
        # self.assertInNodeText("reacted", "#discussion .replies .reply[data-emojis=heart]")

class PortfolioProjectTests(OrganizationSiteFunctionalTests):

    def _fill_in_signup_form(self, email, username=None):
        if username:
            self.fill_field("#id_username", username)
        else:
            self.fill_field("#id_username", "test+%s@q.govready.com" % get_random_string(8))
        self.fill_field("#id_email", email)
        new_test_user_password = get_random_string(16)
        self.fill_field("#id_password1", new_test_user_password)
        self.fill_field("#id_password2", new_test_user_password)

    def test_create_portfolios(self):
        # Create a new account
        self.browser.get(self.url("/"))
        self.click_element('#tab-register')
        self._fill_in_signup_form("test+account@q.govready.com", "portfolio_user")
        self.click_element("#signup-button")

        # Go to portfolio page
        self.browser.get(self.url("/portfolios"))

        # Navigate to portfolio created on signup
        self.click_element_with_link_text("portfolio-user")
        var_sleep(0.5)

        # Test creating a portfolio using the form
        # Navigate to the portfolio form
        self.click_element_with_link_text("Portfolios")
        # Click Create Portfolio button
        self.click_element("#new-portfolio")
        var_sleep(0.25)
        # Fill in form
        self.fill_field("#id_title", "Test 1")
        self.fill_field("#id_description", "Test 1 portfolio")
        # Submit form
        self.click_element("#create-portfolio-button")
        # Test we are on portfolio page we just created
        var_sleep(0.35)
        self.assertRegex(self.browser.title, "Test 1 Portfolio - GovReady-Q")

        # Test we cannot create a portfolio with the same name
        # Navigate to the portfolio form
        self.click_element_with_link_text("Portfolios")
        # Click Create Portfolio button
        self.click_element("#new-portfolio")
        var_sleep(0.25)
        # Fill in form
        self.fill_field("#id_title", "Test 1")
        self.fill_field("#id_description", "Test 1 portfolio")
        # Submit form
        self.click_element("#create-portfolio-button")
        # We should get an error
        var_sleep(0.25)
        # test error
        self.assertIn("Portfolio name Test 1 not available.", self._getNodeText("div.alert.alert-danger.alert-dismissable.alert-link"))
        # Test uniqueness with case insentivity
        # Navigate to the portfolio form
        self.click_element_with_link_text("Portfolios")
        # Click Create Portfolio button
        self.click_element("#new-portfolio")
        var_sleep(0.25)
        # Fill in form
        self.fill_field("#id_title", "test 1")
        # Submit form
        var_sleep(0.5)
        self.click_element("#create-portfolio-button")
        # We should get an error
        var_sleep(0.25)
        # test error
        self.assertIn("Portfolio name test 1 not available.", self._getNodeText("div.alert.alert-danger.alert-dismissable.alert-link"))

    def test_create_portfolio_project(self):
        # Create new project within portfolio
        self._login()
        self._new_project()
        var_sleep(0.5)

        # Create new portfolio
        self.browser.get(self.url("/portfolios"))
        var_sleep(0.5)
        self.click_element("#new-portfolio")
        self.fill_field("#id_title", "Security Projects")
        self.fill_field("#id_description", "Project Description")
        self.click_element("#create-portfolio-button")
        var_sleep(1.75)
        self.assertRegex(self.browser.title, "Security Projects")

    def test_create_project_without_portfolio(self):
        self._login()
        self.browser.get(self.url("/store"))
        self.assertInNodeText("Please select 'Start a project' to continue.", ".alert-danger")

    def test_grant_portfolio_access(self):
        # Grant another member access to portfolio
        self._login()
        self.browser.get(self.url("/portfolios"))
        self.click_element("#portfolio_{}".format(self.user.username))
        self.click_element("#grant-portfolio-access")
        var_sleep(1.25)
        self.select_option_by_visible_text('#invite-user-select', 'me2')
        var_sleep(0.75)
        self.click_element("#invitation_modal button.btn-submit")
        var_sleep(1)
        self.assertInNodeText("me2", "#portfolio-member-me2")

        # Grant another member ownership of portfolio
        var_sleep(0.5)
        self.click_element("#me2_grant_owner_permission")
        var_sleep(0.5)
        self.assertInNodeText("me2 (Owner)", "#portfolio-member-me2")

       # Grant another member access to portfolio
        self.click_element("#grant-portfolio-access")
        self.select_option_by_visible_text('#invite-user-select', 'me3')
        self.click_element("#invitation_modal button.btn-submit")
        var_sleep(0.5)
        self.assertInNodeText("me3", "#portfolio-member-me3")

        # Remove another member access to portfolio
        self.click_element("#me3_remove_permissions")
        self.assertNotInNodeText("me3", "#portfolio-members")
        self.assertNodeNotVisible("#portfolio-member-me3")

    def test_move_project_create(self):
            """Test moving a project to another portfolio"""
            initial_porfolio = Portfolio.objects.create(title="Portfolio 1")
            new_portfolio = Portfolio.objects.create(title="Portfolio 2")
            project = Project.objects.create(portfolio=initial_porfolio)
            project.portfolio = initial_porfolio
            self.assertIsNotNone(initial_porfolio.id)
            self.assertIsNotNone(new_portfolio.id)
            self.assertIsNotNone(project.id)
            self.assertIsNotNone(project.portfolio.id)
            self.assertEqual(project.portfolio.title,"Portfolio 1")
            project.portfolio = new_portfolio
            self.assertEqual(project.portfolio.title,"Portfolio 2")
            project.delete()
            self.assertTrue(project.id is None)

    def test_edit_portfolio(self):
        """
        Editing a portfolio's title and/or description provides appropriate validation and messaging
        """
        # journey to portfolios and ensure i have multiple portfolios if not then create new portfolios
        self._login()
        self.browser.get(self.url("/portfolios"))
        # Navigate to the portfolio form
        self.click_element_with_link_text("Portfolios")
        # Click Create Portfolio button
        self.click_element("#new-portfolio")
        var_sleep(0.25)
        # Fill in form
        self.fill_field("#id_title", "Test 1")
        self.fill_field("#id_description", "Test 1 portfolio")
        # Submit form
        self.click_element("#create-portfolio-button")
        # Test we are on portfolio page we just created
        var_sleep(0.35)
        self.assertRegex(self.browser.title, "Test 1 Portfolio - GovReady-Q")
        # Navigate to portfolios
        self.browser.get(self.url("/portfolios"))
        # Assert we have the new portfolio
        self.assertIn("Test 1", self._getNodeText("#portfolio_Test\ 1"))

        # Click on the pencil anchor tag to edit the newly created portfolio
        self.browser.find_elements_by_class_name("portfolio-project-link")[-1].click()

        # test editing the title to be the same as another portfolio title. Check for validation error message Portfolio with this Title already exists.
        # Fill in form
        self.clear_and_fill_field("#id_title", "me")
        # Submit form
        self.click_element("#edit_portfolio_submit")
        # We should get an error
        var_sleep(0.25)
        # test error
        self.assertIn("Portfolio name me not available.", self._getNodeText("div.alert.fade.in.alert-danger"))

        # Navigate to portfolios
        self.browser.get(self.url("/portfolios"))
        # Click on the pencil anchor tag to edit
        self.browser.find_elements_by_class_name("portfolio-project-link")[-1].click()

        # Edit title to a real new name and press update
        self.clear_and_fill_field("#id_title", "new me")
        self.clear_and_fill_field("#id_description", "new me portfolio")
        # Submit form
        self.click_element("#edit_portfolio_submit")

        # Verify new portfolio name is listed under portfolios
        self.assertIn("new me", self._getNodeText("#portfolio_new\ me"))
        # Verify 'updated' message is correct
        self.assertIn("The portfolio 'new me' has been updated.", self._getNodeText("div.alert.fade.in.alert-info"))

        # verify new description by journeying back to edit_form
        self.browser.find_elements_by_class_name("portfolio-project-link")[-1].click()
        self.assertIn("new me portfolio", self.browser.find_element_by_css_selector("#id_description").get_attribute('value'))

    def test_delete_portfolio(self):
        """
        Delete a portfolio from the database
        """
        portfolio = Portfolio.objects.all().first()
        # Login and journey to portfolios
        self._login()
        self.browser.get(self.url("/portfolios"))
        # Hit deletion pattern
        self.browser.get(self.url(f"/portfolios/{portfolio.id}/delete"))

        # Verify 'deleted' message is correct
        self.assertIn("The portfolio 'me' has been deleted.", self._getNodeText("div.alert.fade.in.alert-info"))

class QuestionsTests(OrganizationSiteFunctionalTests):

    def _test_api_get(self, path, expected_value):
        resp = self.client_get(
                "/api/v1/projects/" + str(self.current_project.id) + "/answers",
                HTTP_AUTHORIZATION=self.user.api_key_rw)
        resp = resp.json()
        self.assertTrue(isinstance(resp, dict))
        self.assertEqual(resp.get("schema"), "GovReady Q Project API 1.0")
        for p in ["project"]+path:
            self.assertTrue(isinstance(resp, dict))
            self.assertIn(p, resp)
            resp = resp[p]
        self.assertEqual(resp, expected_value)

    def test_questions_text(self):
        # Log in and create a new project.
        var_sleep(.5)
        self._login()
        var_sleep(.5)
        self._new_project()
        self.click_element('#question-question_types_text')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # Click interstital "Got it" button
        self.click_element("#save-button")
        var_sleep(.5)

        # text
        self.assertIn("| Test The Text Input Question Types - GovReady-Q", self.browser.title)
        self.fill_field("#inputctrl", "This is some text.")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_text"], "This is some text.")

        # text w/ default
        self.assertRegex(self.browser.title, "Next Question: text_with_default")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_text_with_default"], "I am a kiwi.")

        # password-type question input (this is not a user pwd)
        self.assertRegex(self.browser.title, "Next Question: password")
        self.fill_field("#inputctrl", "th1s1z@p@ssw0rd!")
        self.click_element("#save-button")
        var_sleep(1)
        self._test_api_get(["question_types_text", "q_password"], "th1s1z@p@ssw0rd!")

        # email-address
        self.assertRegex(self.browser.title, "Next Question: email-address")

        # test a bad address
        self.fill_field("#inputctrl", "a@a")
        self.click_element("#save-button")
        var_sleep(1.0)
        self.assertInNodeText("is not valid.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

        # test a good address
        val = "test+%s@q.govready.com" % get_random_string(8)
        self.clear_and_fill_field("#inputctrl", val)
        self.click_element("#save-button")
        var_sleep(1.5)
        self._test_api_get(["question_types_text", "q_email_address"], val)

        # url
        self.assertRegex(self.browser.title, "Next Question: url")

        # test a bad address
        self.clear_and_fill_field("#inputctrl", "example.x")
        self.click_element("#save-button")
        # This is caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.
        self.assertRegex(self.browser.title, "Next Question: url")

        # test a good address
        self.clear_and_fill_field("#inputctrl", "https://q.govready.com")
        self.click_element("#save-button")
        var_sleep(1.5)
        self._test_api_get(["question_types_text", "q_url"], "https://q.govready.com")

        # longtext
        self.assertRegex(self.browser.title, "Next Question: longtext")
        self.fill_field("#inputctrl .ql-editor", "This is a paragraph.\n\nThis is another paragraph.")
        self.click_element("#save-button")
        var_sleep(1.0)
        self._test_api_get(["question_types_text", "q_longtext"], 'This is a paragraph\\.\n\n\n\nThis is another paragraph\\.')
        self._test_api_get(["question_types_text", "q_longtext.html"], "<p>This is a paragraph.</p>\n<p>This is another paragraph.</p>")

        # longtext w/ default
        self.assertRegex(self.browser.title, "Next Question: longtext_with_default")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_longtext_with_default"], "Peaches are sweet\\.\n\nThat\\'s why I write two paragraphs about peaches\\.")
        self._test_api_get(["question_types_text", "q_longtext_with_default.html"], "<p>Peaches are sweet.</p>\n<p>That's why I write two paragraphs about peaches.</p>")

        # date
        self.assertRegex(self.browser.title, "Next Question: date")

        # test a bad date
        self.select_option("select[name='value_year']", "2016")
        self.select_option("select[name='value_month']", "2")
        self.select_option("select[name='value_day']", "31")
        self.click_element("#save-button")
        var_sleep(.5)
        self.assertInNodeText("day is out of range for month", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # test a good date
        self.select_option("select[name='value_year']", "2016")
        self.select_option("select[name='value_month']", "8")
        self.select_option("select[name='value_day']", "22")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_date"], "2016-08-22")

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Text Input Question Types - ")
        # Need new tests for testing text appeared in linked output document instead of on the finished page as we use to test below
        # self.assertInNodeText("I am a kiwi.", "#document-1-body") # text default should appear
        # self.assertInNodeText("Peaches are sweet.", "#document-1-body") # text default should appear

    def test_questions_choice(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_choice')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # Click interstital "Got it" button
        self.click_element("#save-button")
        var_sleep(.5)

        # choice
        self.assertIn("| Test The Choice Question Types - GovReady-Q", self.browser.title)
        self.click_element('#question input[name="value"][value="choice2"]')
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_choice", "q_choice"], "choice2")
        self._test_api_get(["question_types_choice", "q_choice.text"], "Choice 2")

        # yesno
        self.assertRegex(self.browser.title, "Next Question: yesno")
        self.click_element('#question input[name="value"][value="yes"]')
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_choice", "q_yesno"], "yes")
        self._test_api_get(["question_types_choice", "q_yesno.text"], "Yes")

        # multiple-choice
        self.assertRegex(self.browser.title, "Next Question: multiple-choice")
        self.click_element('#question input[name="value"][value="choice1"]')
        self.click_element('#question input[name="value"][value="choice3"]')
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_choice", "q_multiple_choice"], ["choice1", "choice3"])
        self._test_api_get(["question_types_choice", "q_multiple_choice.text"], ["Choice 1", "Choice 3"])

        # datagrid
        # self.assertRegex(self.browser.title, "Next Question: datagrid")
        # self.click_element('#question input[name="value"][value="field1"]')
        # self.click_element('#question input[name="value"][value="field3"]')
        # self.click_element("#save-button")
        # var_sleep(.5)
        # self._test_api_get(["question_types_field", "q_datagrid"], ["field1", "field3"])
        # self._test_api_get(["question_types_field", "q_datagrid.text"], ["Field 1", "Field 3"])

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Choice Question Types - ")

    def test_questions_numeric(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_numeric')

        # Introduction screen.
        var_sleep(0.75)
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # integer
        self.assertIn("| Test The Numeric Question Types - GovReady-Q", self.browser.title)

        # Click interstital "Got it" button
        self.click_element("#save-button")
        var_sleep(.5)

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Invalid input. Must be a whole number.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a string.
        self.clear_and_fill_field("#inputctrl", "asdf")
        self.click_element("#save-button")
        var_sleep(.5)

        # This is caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.
        self.assertIn("| Test The Numeric Question Types - GovReady-Q", self.browser.title)
        var_sleep(.5)

        # Test a good integer.
        self.clear_and_fill_field("#inputctrl", "5000")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_integer"], 5000)

        # integer min/max
        self.assertRegex(self.browser.title, "Next Question: integer min/max")

        # Test a too-small number
        self.clear_and_fill_field("#inputctrl", "0")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at least 1.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a too-large number
        self.clear_and_fill_field("#inputctrl", "27")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at most 10.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(.5)

        # This should be caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.
        self.assertRegex(self.browser.title, "Next Question: integer min/max")
        var_sleep(.5)

        # Test a good integer.
        self.clear_and_fill_field("#inputctrl", "3")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_integer_minmax"], 3)

        # integer min/max big
        # For max > 1000, we should expect that we can use commas in our numbers
        # so we need to do slightly different tests.

        self.assertRegex(self.browser.title, "Next Question: integer min/max big")

        # Test a too-small number
        self.clear_and_fill_field("#inputctrl", "0")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at least 1.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a too-large number
        self.clear_and_fill_field("#inputctrl", "15000")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at most 10000.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Invalid input. Must be a whole number.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a good integer that has a comma in it.
        self.clear_and_fill_field("#inputctrl", "1,234")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_integer_minmax_big"], 1234)

        # real
        self.assertRegex(self.browser.title, "Next Question: real")

        # Test a string.
        self.clear_and_fill_field("#inputctrl", "asdf")
        self.click_element("#save-button")
        var_sleep(.5)

        # This is caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.
        self.assertRegex(self.browser.title, "Next Question: real")

        # Test a real number.
        self.clear_and_fill_field("#inputctrl", "1.050")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_real"], 1.050)

        # real min/max
        self.assertRegex(self.browser.title, "Next Question: real min/max")

        # Test a number that's too small.
        self.clear_and_fill_field("#inputctrl", "0.01")
        self.click_element("#save-button")
        var_sleep(.5)
        # var_sleep(60)
        self.assertInNodeText("Must be at least 1.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a number that's too large.
        self.clear_and_fill_field("#inputctrl", "1000")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at most 100.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.

        # Test a real number.
        self.clear_and_fill_field("#inputctrl", "23.051")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_real_minmax"], 23.051)

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Numeric Question Types - ")

    def test_questions_media(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_media')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # file upload
        self.assertIn("| Test The Media Question Types - GovReady-Q", self.browser.title)

        # Click interstital "Got it" button
        self.click_element("#save-button")
        var_sleep(.5)

        # We need to upload a file that we know exists.
        testFilePath = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fixtures',
            'testimage.png'
        )
        if DOS:
            testFilePath = convert_w(testFilePath)
        var_sleep(1)
        self.fill_field("#inputctrl", testFilePath)

        self.click_element("#save-button")
        var_sleep(1)

        # Clicking the global modal error ok button
        self.browser.find_element_by_xpath("//*[@id='global_modal']/div/div/div[3]/button[1]").click()

        # interstitial
        # nothing to really test in terms of functionality, but check that
        # page elements are present
        self.assertIn("| Test The Media Question Types - GovReady-Q", self.browser.title)
        self.assertInNodeText("Upload a file!", "h1")

        self.click_element("#save-button")
        # TODO: commenting out for now they are not passing
       # self.assertRegex(self.browser.title, "^Test The Media Question Types - ")
       # self.assertInNodeText("Download attachment (image; 90.5 kB; ",
            #   ".output-document div[data-question='file']")

    def test_questions_module(self):
        # Log in and create a new project.
        var_sleep(.5)
        self._login()
        var_sleep(.5)
        self._new_project()
        # start "Test The Module Question Types"
        self.click_element('#question-question_types_module')
        var_sleep(1.5)

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.75)

        # "You will now begin a module."
        self.assertIn("| Test The Module Question Types - GovReady-Q", self.browser.title)
        self.click_element("#save-button")
        var_sleep(.75)

        # We're now at the intro screen for the simple sub-module.
        # Grab the page URL here so we can figure out the ID of this task
        # so that we can select it again later.
        var_sleep(3.0)
        import urllib.parse
        s = urllib.parse.urlsplit(self.browser.current_url)
        m = re.match(r"^/tasks/(\d+)/", s[2])
        task_id = int(m.group(1))

        def do_submodule(answer_text):
            var_sleep(1.25)
            self.assertRegex(self.browser.title, "Next Question:")
            self.click_element("#save-button")
            var_sleep(3)
            self.assertRegex(self.browser.title, "Next Question: The Question")
            self.fill_field("#inputctrl", answer_text)
            self.click_element("#save-button")
            var_sleep(1.25)
            self.assertRegex(self.browser.title, "^A Simple Module - ")

            # Return to the main module.
            self.click_element("#return-to-supertask")
            var_sleep(1.25)

        do_submodule("My first answer.")
        self.assertRegex(self.browser.title, "^Test The Module Question Types - ")
        # Go back to the question and start a second answer.
        def change_answer():
            print("change_answer() - self.click_element(\"#link-to-question-q_module a\")") #debug
            self.click_element("#link-to-question-q_module a")
        change_answer()
        self.assertIn("| Test The Module Question Types - GovReady-Q", self.browser.title)
        self.click_element('#question input[name="value"][value="__new"]')
        self.click_element("#save-button")
        var_sleep(2.25)
        do_submodule("My second answer.")
        self.assertRegex(self.browser.title, "^Test The Module Question Types - ")

        # Go back and change the answer to the first one again.
        change_answer()
        self.assertRegex(self.browser.title, "Next Question: module")
        self.click_element('#question input[name="value"][value="%d"]' % task_id)
        self.click_element("#save-button")
        var_sleep(.5)
        self.assertRegex(self.browser.title, "Test The Module Question Types - ")

class OrganizationSettingsTests(OrganizationSiteFunctionalTests):

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")
        var_sleep(0.5)

    def test_settings_page(self):
        # Log in
        var_sleep(.5)
        self._login()
        # test navigating to settings page not logged in
        self.browser.get(self.url("/settings"))
        self.assertRegex(self.browser.title, "GovReady-Q")
        self.assertNotRegex(self.browser.title, "GovReady Setup")
        var_sleep(0.5)

        # login as user without admin privileges and test settings page unreachable
        self.browser.get(self.url("/accounts/logout/"))
        self._login(self.user2.username, self.user2.clear_password)
        self.browser.get(self.url("/projects"))
        var_sleep(1)

        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 403)

        # logout
        self.browser.get(self.url("/accounts/logout/"))

        # login as user with admin privileges access settings page
        self._login()
        self.browser.get(self.url("/settings"))
        self.assertRegex(self.browser.title, "GovReady-Q Setup")
        var_sleep(1)

        print("self.user is '{}'".format(self.user))
        print("self.user.username is '{}'".format(self.user.username))
        print("self.user2.username is '{}'".format(self.user2.username))

        # SAMPLE NAVIGATING AND TESTING
        # text
        # self.assertRegex(self.browser.title, "Next Question: text")
        # self.fill_field("#inputctrl", "This is some text.")
        # self.click_element("#save-button")
        # var_sleep(.5)
        # self._test_api_get(["question_types_text", "q_text"], "This is some text.")

        # # text w/ default
        # self.assertRegex(self.browser.title, "Next Question: text_with_default")
        # self.click_element("#save-button")
        # var_sleep(.5)
        # self._test_api_get(["question_types_text", "q_text_with_default"], "I am a kiwi.")
        # # email-address
        # self.assertRegex(self.browser.title, "Next Question: email-address")
