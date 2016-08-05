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

# Would be nice to run this without setting up a DB
# see: http://stackoverflow.com/questions/5917587/django-unit-tests-without-a-db
# however, we can test settings w/o having to worry about mysql

class TestDefaultSettings(SimpleTestCase):
    def test_db_is_local(self):
        db_is = settings.DATABASES['default']['ENGINE']
        db_should_be = 'django.db.backends.sqlite3'
        self.assertEqual(db_is, db_should_be)

    def test_secret_key(self):
        self.assertIsNotNone(settings.SECRET_KEY)

    def test_misc_local_settings(self):
        self.assertEqual(settings.DEBUG, False)

    def test_misc_default_settings(self):
        # because the SeleniumTests change settings.ALLOWED_HOSTS,
        # we can't test that - it's dependent on the order in which the tests run
        #self.assertEqual(settings.ALLOWED_HOSTS, ['*'], "This seems like a bug")
        self.assertListEqual(settings.ADMINS,[])

    # it may not be possible as
    #    manage.py test siteapp
    # initializes all the setting before processing any of this.
    @skip("Skip CloudFormation tests until later")
    def test_only_cf_settings(self):
        skipTest("Not yet")
        self.assertEqual(settings.HTTPS, False)
        self.assertEqual(settings.HOST, "localhost:8000")
        self.assertIsNone(settings.USE_MEMCACHED)
        self.assertIsNone(settings.EMAIL)
        self.assertIsNone(settings.STATIC)

    def test_pre_cf_settings(self):
        self.assertRegexpMatches(
            settings.CACHES['default']['BACKEND'],
            'django.core.cache.backends.locmem.LocMemCache',
            "Default is to use LocMemCache, unless explictly using 'memcached'"
        )
        self.assertRegexpMatches(settings.EMAIL_SUBJECT_PREFIX, '[localhost:8000]', "Uses environment[host]")
        self.assertEqual(settings.EMAIL_BACKEND, 'django.core.mail.backends.locmem.EmailBackend', "Based on environment.get('email')")
        self.assertFalse(settings.SESSION_COOKIE_SECURE, "Based on environment[https]")
        self.assertIsNone(settings.STATIC_ROOT, "Based on environment.get('static')")
        # because the SeleniumTests change settings.ALLOWED_HOSTS,
        # we can't test that - it's dependent on the order in which the tests run
        #self.assertEqual(settings.SITE_ROOT_URL, "http://localhost:8000", "Based on environment[https]")

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
        u = User.objects.create(username="me")
        u.set_password("1234")
        u.save()
        ProjectMembership.objects.get_or_create(user=u, project=org.get_organization_project())

        # And initialize the root Task of the Organization with this user as its editor.
        org.get_organization_project().set_root_task("organization", u)

    def url(self, path):
        # Within this test, we only generate URLs for the organization subdomain.
        return super().url("testorg", path)

    def _login(self, is_first_time_user=True, is_first_time_org=False):
        # Fill in the login form and submit.
        self.browser.get(self.url("/")) # redirects to /accounts/login/

        self.assertRegex(self.browser.title, "Sign In")
        self.fill_field("#id_login", "me")
        self.fill_field("#id_password", "1234")
        self.click_element("form button.primaryAction")

        # If this is the user's first login, then we are now at the
        # user account settings task. Proceed through those questions.
        if is_first_time_user:
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
            self.browser.get(self.url("/"))

        if is_first_time_org:
            # The first time we hit an Organization home, we are
            # taken to its org info task.
            var_sleep(.5) # wait for page to load
            self.assertIn("Introduction | Organization Classification", self.browser.title)

            # - The user is looking at the Introduction page.
            self.click_element("#save-button")
            var_sleep(.5) # wait for page to load

            # - Now at the 'what kind of org is it' page?
            self.click_element("input[value='smbiz']")
            self.click_element("#save-button")
            var_sleep(.5) # wait for page to load

            # - We're on the module finished page.
            self.browser.get(self.url("/"))

        self.assertRegex(self.browser.title, "Home")

    def _new_project(self):
        self.browser.get(self.url("/"))
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
        self._login(is_first_time_user=True, is_first_time_org=True)
        self.browser.get(self.url("/accounts/logout/"))
        self._login(is_first_time_user=False)

    def test_simple_module(self):
        # Log in and create a new project and start its task.
        self._login(is_first_time_user=True, is_first_time_org=True)
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
        self.assertRegex(self.browser.title, "^A Simple Module - GovReady Q$")

    def test_invitations(self):
        # Test a bunch of invitations.

        # Log in and create a new project.
        self._login(is_first_time_user=True, is_first_time_org=True)
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
            self._login(is_first_time_user=False)
            self.browser.get(project_page)

        # Test an invitation to that project.
        self.click_element("#project-settings-tab a")
        self.click_element("#invite-user-to-project")
        do_invitation("test+project@q.govready.com")
        self.assertRegex(self.browser.title, "My Simple Project") # user is on the project page
        self.click_element('#question-simple_module .task-item a') # go to the task page
        self.assertRegex(self.browser.title, "A Simple Module") # user is on the task page
        self.assertInNodeText("is editing this module. You cannot make changes to it.", "#auth-status .text-danger")

        reset_login()

        # Test an invitation to take over editing a task but without joining the project.
        self.click_element('#question-simple_module .task-item a') # go to the task page
        var_sleep(.5) # wait for page to load
        self.click_element("#save-button") # pass over the Introductory question because the Ask Team button is suppressed on interstitials
        var_sleep(.5) # wait for page to load
        self.click_element("#ask-team-show-options")
        var_sleep(.5) # wait for options to slideDown
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
        # Log in and create a new project.
        self._login(is_first_time_user=True, is_first_time_org=True)
        self._new_project()
        self._start_task()

        # Move past the introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5) # wait for page to reload

        # We're now on the first actual question.
        # Start a team conversation.
        self.click_element("#ask-team-show-options")
        var_sleep(.5) # wait for options to slideDown
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

        # This takes the user directly to the discussion they were invited to join.
        # Leave a comment.
        self.fill_field("#discussion-your-comment", "Yes it's me!\n\nI am here with you.")
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(.5) # wait for it to submit

        # Leave an emoji reaction on the initial user's comment.
        self.click_element("#react-with-emoji")
        var_sleep(.5) # emoji selector shows
        self.click_element("#emoji-selector .emoji[data-emoji-name=heart]") # makes active
        self.click_element("body") # closes emoji panel and submits via ajax
        var_sleep(.5) # emoji reaction submitted

        var_sleep(5)

        # Log back in as the original user.
        discussion_page = self.browser.current_url
        self.browser.get(self.url("/accounts/logout/"))
        self._login(is_first_time_user=False)
        self.browser.get(discussion_page)

        # Test that we can see the comment and the reaction.
        self.assertInNodeText("Yes it's me!", "#discussion .comment:not(.author-is-self) .comment-text")
        self.assertInNodeText("reacted", "#discussion .reactions .reply[data-emojis=heart]")
