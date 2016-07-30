from django.conf import settings
from django.test import SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from unittest import skip

import re
from time import sleep

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
        self.assertEqual(settings.ALLOWED_HOSTS, ['*'], "This seems like a bug")
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
        self.assertEqual(settings.SITE_ROOT_URL, "http://localhost:8000", "Based on environment[https]")

class SeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTest, cls).setUpClass()

        # Override the email backend so that we can capture sent emails.
        from django.conf import settings
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        # Override ALLOWED_HOSTS and SITE_ROOT_URL because we use this to parse
        # the Organizational subdomain of each request and it may not be set or
        # set properly in the local environment's non-test settings.
        settings.ALLOWED_HOSTS = ['.localhost']
        settings.SITE_ROOT_URL = cls.live_server_url

        # Turn on DEBUG so we can see errors better.
        settings.DEBUG = True

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
        base_url = urllib.parse.urlunsplit((s[0], ((subdomain+'.') if subdomain else "")+s[1], '', '', ''))
        return urllib.parse.urljoin(base_url, path)

    def fill_field(self, css_selector, text):
        self.browser.find_element_by_css_selector(css_selector).send_keys(text)

    def click_element(self, css_selector):
        self.browser.find_element_by_css_selector(css_selector).click()

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

    def url(self, path):
        # Within this test, we only generate URLs for the organization subdomain.
        return super().url("testorg", path)
    
    def _login(self, is_first_time=True):
        # Fill in the login form and submit.
        self.browser.get(self.url("/")) # redirects to /accounts/login/

        self.assertRegex(self.browser.title, "Sign In")
        self.fill_field("#id_login", "me")
        self.fill_field("#id_password", "1234")
        self.click_element("form button.primaryAction")

        # If this is the user's first login, then we are now at the
        # user account settings task. Proceed through those questions.
        if is_first_time:
            sleep(.5) # wait for page to load
            self.assertIn("Introduction", self.browser.title)

            # - The user is looking at the Introduction page.
            self.click_element("#save-button")
            sleep(.5) # wait for page to load

            # - Now at the what is your name page?
            self.fill_field("#inputctrl", "John Doe")
            self.click_element("#save-button")
            sleep(.5) # wait for page to load

            # - We're on the module finished page.
            self.browser.get(self.url("/"))

        self.assertRegex(self.browser.title, "Home")

    def _new_project(self):
        self.browser.get(self.url("/"))
        self.click_element("#new-project")
        self.fill_field("#id_title", "My Simple Project")
        self.click_element("#id_module_id_0")
        self.click_element("button[type=submit]")
        sleep(1)
        self.assertRegex(self.browser.title, "My Simple Project")

    def _start_task(self):
        # Assumes _new_project() just finished.
        
        # Start the task.
        self.click_element('#question-simple_module .task-commands form a')

    def _accept_invitation(self):
        # Assumes an invitation email was sent.

        # Extract the URL in the email and visit it.
        invitation_body = self.pop_email().body
        invitation_url_pattern = re.escape(self.url("/invitation/")) + r"\S+"
        self.assertRegex(invitation_body, invitation_url_pattern)
        m = re.search(invitation_url_pattern, invitation_body)
        self.browser.get(m.group(0))

        # We're at the sign-in page. Go to the create account page
        # and register.
        self.assertRegex(self.browser.title, "Sign In")
        self.click_element("p a") # This isn't a very good targetting of the "sign up" link.
        sleep(.5) # wait for page to load
        self.fill_field("#id_username", "you")
        self.fill_field("#id_email", "test+account@q.govready.com")
        self.fill_field("#id_password1", "1234")
        self.fill_field("#id_password2", "1234")
        self.click_element("form.signup button") # This isn't a very good targetting of the "sign up" link.
        sleep(.5) # wait for next page to load

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "GovReady Q")

    def test_login(self):
        # Log in as a new user, log out, then log in a second time.
        # We should only get the account settings questions on the
        # first login.
        self._login(is_first_time=True)
        self.browser.get(self.url("/accounts/logout/"))
        self._login(is_first_time=False)

    def test_simple_module(self):
        # Log in and create a new project and start its task.
        self._login(is_first_time=True)
        self._new_project()
        self._start_task()

        # Answer the questions.

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        sleep(.5)

        # Text question.
        self.assertRegex(self.browser.title, "Next Question: The Question")
        self.fill_field("#inputctrl", "This is some text.")
        self.click_element("#save-button")
        sleep(.5)

        # Finished.
        self.assertRegex(self.browser.title, "^A Simple Module - GovReady Q$")

    def test_discussion(self):
        # Log in and create a new project.
        self._login(is_first_time=True)
        self._new_project()
        self._start_task()

        # Move past the introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        sleep(.5) # wait for page to reload

        # We're now on the first actual question.
        # Start a team conversation.
        self.click_element("#ask-team-show-options")
        sleep(.5) # wait for options to slideDown
        self.click_element("#start-a-discussion a")
        self.fill_field("#discussion-your-comment", "Hello is anyone *here*?")
        self.click_element("#discussion .comment-input button.btn-primary")

        # Invite a guest to join.
        sleep(.5) # wait for the you-are-alone div to show
        self.click_element("#discussion-you-are-alone a")
        sleep(.5) # wait for modal to show
        self.fill_field("#invitation_modal #invite-user-email", "invited-user@q.govready.com")
        self.click_element("#invitation_modal button.btn-submit")
        sleep(1) # wait for invitation to be sent

        # Now we become that guest. Log out.
        # Then accept the invitation as an anonymous user.
        self.browser.get(self.url("/accounts/logout/"))
        self._accept_invitation()

        # This takes the user directly to the discussion they were invited to join.
        # Leave a comment.
        self.fill_field("#discussion-your-comment", "Yes it's me!\n\nI am here with you.")
        self.click_element("#discussion .comment-input button.btn-primary")
        sleep(.5) # wait for it to submit

        # Leave an emoji reaction on the initial user's comment.
        self.click_element("#react-with-emoji")
        sleep(.5) # emoji selector shows
        self.click_element("#emoji-selector .emoji[data-emoji-name=heart]") # makes active
        self.click_element("body") # closes emoji panel and submits via ajax
        sleep(.5) # emoji reaction submitted

        sleep(5)

        # Log back in as the original user.
        discussion_page = self.browser.current_url
        self.browser.get(self.url("/accounts/logout/"))
        self._login(is_first_time=False)
        self.browser.get(discussion_page)

        # Test that we can see the comment and the reaction.
        self.assertIn("Yes it's me!", self.browser.find_element_by_css_selector("#discussion .comment:not(.author-is-self) .comment-text").text)
        self.assertIn("reacted", self.browser.find_element_by_css_selector("#discussion .reactions .reply[data-emojis=heart]").text)
        