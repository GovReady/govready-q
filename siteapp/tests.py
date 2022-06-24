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
import time
import unittest
import json

from django.contrib.auth import authenticate
from django.test.client import RequestFactory

import selenium.webdriver
from selenium.webdriver.remote.command import Command
from django.urls import reverse
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from django.contrib.auth.models import Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# StaticLiveServerTestCase can server static files but you have to make sure settings have DEBUG set to True
from django.utils.crypto import get_random_string
from django import db

from controls.enums.statements import StatementTypeEnum
from guidedmodules.tests import TestCaseWithFixtureData
from siteapp.models import (Organization, Portfolio, Project,
                            ProjectMembership, User)
from controls.models import Statement, Element, System
from controls.oscal import CatalogData, Catalogs, Catalog
from siteapp.settings import HEADLESS, DOS, DOCKER, SELENIUM_BROWSER
from siteapp.views import project_edit
from tools.utils.linux_to_dos import convert_w
from urllib.parse import urlparse


def var_sleep(duration):
    '''
    Tweak sleep globally by multiple, a fraction, or depend on env
    '''
    from time import sleep
    sleep(duration * 2)


def wait_for_sleep_after(fn):
    MAX_WAIT = 20
    start_time = time.time()
    while True:
        try:
            return fn()
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.5)


class SeleniumTest(StaticLiveServerTestCase):
    window_geometry = (1200, 1200)

    @classmethod
    def setUpClass(cls):
        if DOCKER and not HEADLESS:
            # Prevents auto localhost:random_port for remote docker selenium-grid
            # cls.port = 8001
            cls.host = "govready-q-dev"

        super(SeleniumTest, cls).setUpClass()

        # Override the email backend so that we can capture sent emails.
        from django.conf import settings
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

        # Override ALLOWED_HOSTS, SITE_ROOT_URL, etc.
        # because they may not be set or set properly in the local environment's
        # non-test settings for the URL assigned by the LiveServerTestCase server.
        # StaticLiveServerTestCase can server static files but you have to make sure settings have DEBUG set to True
        settings.ALLOWED_HOSTS = ['localhost', 'testserver', "govready-q-dev"]
        settings.SITE_ROOT_URL = cls.live_server_url
        settings.DEBUG = True

        # In order for these tests to succeed when not connected to the
        # Internet, disable email deliverability checks which query DNS.
        settings.VALIDATE_EMAIL_DELIVERABILITY = False

        ## Turn on DEBUG so we can see errors better.
        #settings.DEBUG = True

        # Start a headless browser.

        option_map = {
            "chrome": (selenium.webdriver.ChromeOptions, DesiredCapabilities.CHROME),
            "firefox": (selenium.webdriver.FirefoxOptions, DesiredCapabilities.FIREFOX),
            "opera": (selenium.webdriver.ChromeOptions, DesiredCapabilities.OPERA),
        }
        option = option_map[SELENIUM_BROWSER]
        options = option[0]()
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        options.add_argument("disable-infobars")  # "Chrome is being controlled by automated test software."
        if SeleniumTest.window_geometry == "maximized":
            options.add_argument("start-maximized")  # too small screens make clicking some things difficult
        else:
            options.add_argument("--window-size=" + ",".join(str(dim) for dim in SeleniumTest.window_geometry))

        options.add_argument("--incognito")

        if DOS:
            # WSL has a hard time finding tempdir so we feed it the dos conversion
            tempfile.tempdir = convert_w(os.getcwd())
        # enable Selenium support for downloads
        cls.download_path = pathlib.Path(tempfile.gettempdir())
        if hasattr(options, 'add_experimental_option'):
            options.add_experimental_option("prefs", {
                "download.default_directory": str(cls.download_path),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
        if HEADLESS:
            options.add_argument('--headless')

        if DOCKER:
            if HEADLESS:
                options.add_argument('--no-sandbox')
                cls.browser = selenium.webdriver.Chrome(chrome_options=options)
            else:
                cls.browser = selenium.webdriver.Remote(command_executor='http://selenium-hub:4444/wd/hub',
                                                        desired_capabilities=option[1],
                                                        options=options)
        else:
            # Depreciated
            # Set up selenium Chrome browser for Windows or Linux
            if DOS:
                # TODO: Find out a way to get chromedriver implicit executable path in WSL
                cls.browser = selenium.webdriver.Chrome(executable_path='chromedriver.exe', options=options)
            else:
                cls.browser = selenium.webdriver.Chrome(chrome_options=options)

        cls.browser.implicitly_wait(5)  # seconds

        # Clean up and quit tests if Q is in SSO mode
        if getattr(settings, 'PROXY_HEADER_AUTHENTICATION_HEADERS', None):
            print("Cannot run tests.")
            print(
                "Tests will not run when IAM Proxy enabled (e.g., when `local/environment.json` sets `trust-user-authentication-headers` parameter.)")
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
        # Add catalogs to database
        CATALOG_PATH = os.path.join(os.path.dirname(__file__),'..','controls','data','catalogs')
        BASELINE_PATH = os.path.join(os.path.dirname(__file__),'..','controls','data','baselines')
        catalog_files = [file for file in os.listdir(CATALOG_PATH) if file.endswith('.json')]
        for cf in catalog_files:
            catalog_key = cf.replace("_catalog.json", "")
            with open(os.path.join(CATALOG_PATH,cf), 'r') as json_file:
                catalog_json = json.load(json_file)
            baseline_filename = cf.replace("_catalog.json", "_baselines.json")
            if os.path.isfile(os.path.join(BASELINE_PATH, baseline_filename)):
                with open(os.path.join(BASELINE_PATH, baseline_filename), 'r') as json_file:
                    baselines_json = json.load(json_file)
            else:
                baselines_json = {}

            catalog, created = CatalogData.objects.get_or_create(
                    catalog_key=catalog_key,
                    catalog_json=catalog_json,
                    baselines_json=baselines_json
                )
            # if created:
            #     print(f"{catalog_key} record created into database")
            # else:
            #     print(f"{catalog_key} record found in database")

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
        self.browser.execute_script(
            "arguments[0].scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });", elem)
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
        node_text = re.sub(r"\s+", " ", node_text)  # normalize whitespace
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
    def setUp(self):
        super().setUp()

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")


class OrganizationSiteFunctionalTests(SeleniumTest):

    def setUp(self):
        super().setUp()

        # Load the Q modules from the fixtures directory.
        from guidedmodules.models import AppSource
        from guidedmodules.management.commands.load_modules import Command as load_modules

        try:
            AppSource.objects.all().delete()
        except Exception as ex:
            print(f"Exception: {ex}")
            print(f"App Sources:{AppSource.objects.all()}")
        AppSource.objects.get_or_create(
            # this one exists on first db load because it's created by
            # migrations, but because the testing framework seems to
            # get rid of it after the first test in this class
            slug="system",
            is_system_source=True,
            defaults={
                "spec": {  # required system projects
                    "type": "local",
                    "path": "fixtures/modules/system",
                }
            }
        )
        var_sleep(1)
        load_modules().handle() # load system modules

        AppSource.objects.get_or_create(
            slug="project",
            spec={  # contains a test project
                "type": "local",
                "path": "fixtures/modules/other",
            },
            trust_assets=True
        )[0].add_app_to_catalog("simple_project")

        # Create a default user that is a member of the organization.
        # Log the user into the test client, which is used for API
        # tests. The Selenium tests require a separate log in via the
        # headless browser.

        var_sleep(2)

        # self.user = User.objects.create_superuser(
        self.user = wait_for_sleep_after(lambda: User.objects.get_or_create(
            username="me",
            email="test+user@q.govready.com",
            is_staff=True
        )[0])
        self.user.clear_password = get_random_string(16)
        self.user.set_password(self.user.clear_password)
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        wait_for_sleep_after(lambda: self.user.save())
        self.user.reset_api_keys()
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.client.login(username=self.user.username, password=self.user.clear_password)

        # Create a Portfolio and Grant Access
        portfolio = Portfolio.objects.get_or_create(title=self.user.username)[0]
        portfolio.assign_owner_permissions(self.user)

        # Create the Organization.
        try:
            self.org = Organization.create(name="Our Organization", slug="testorg",
                                           admin_user=self.user)
        except:
            self.org = Organization.create(name="Our Organization", slug="testorg2",
                                           admin_user=self.user)

        # Set values for default apps (templates) for Aspen new system page
        if "default_appversion_name_list" not in self.org.extra:
            self.org.extra["default_appversion_name_list"] = [
                "Blank Project",
                "Speedy SSP",
                "General IT System ATO for 800-53 (low)"
            ]
            self.org.save()

        # Grant the user permission to change the review state of answers.
        self.org.reviewers.add(self.user)

        # create a second user
        self.user2 = wait_for_sleep_after(lambda: User.objects.get_or_create(
            username="me2",
            email="test+user2@q.govready.com")[0])
        self.user2.clear_password = get_random_string(16)
        self.user2.set_password(self.user2.clear_password)
        self.user2.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        wait_for_sleep_after(lambda: self.user2.save())
        self.user2.reset_api_keys()
        self.user2.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.client.login(username=self.user2.username, password=self.user2.clear_password)
        portfolio = Portfolio.objects.get_or_create(title=self.user2.username)[0]
        portfolio.assign_owner_permissions(self.user2)

        # create a third user
        self.user3 = wait_for_sleep_after(lambda: User.objects.get_or_create(
            username="me3",
            email="test+user3@q.govready.com")[0])
        self.user3.clear_password = get_random_string(16)
        self.user3.set_password(self.user3.clear_password)
        self.user3.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        wait_for_sleep_after(lambda: self.user3.save())
        self.user3.reset_api_keys()
        self.user3.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.client.login(username=self.user3.username, password=self.user3.clear_password)
        portfolio = Portfolio.objects.get_or_create(title=self.user3.username)[0]
        portfolio.assign_owner_permissions(self.user3)

        # Grant second user membership in the organization
        # from https://github.com/GovReady/govready-q/blob/master/siteapp/admin.py#L41
        mb, isnew = ProjectMembership.objects.get_or_create(
            user=self.user2,
            project=self.org.get_organization_project(),
        )

    def client_get(self, *args, **kwargs):
        resp = self.client.get(
            *args, follow=True,
            **kwargs)
        self.assertEqual(resp.status_code, 200, msg=repr(resp))
        return resp  # .content.decode("utf8")

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
        if "Warning Message" in self.browser.title:
            self.click_element("#btn-accept")

    def _new_project(self):
        self.browser.get(self.url("/store"))

        var_sleep(1)
        # Click Add Button
        wait_for_sleep_after(lambda: self.click_element(".app-form[data-app='project/simple_project'] .start-app"))
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "I want to answer some questions on Q."))

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
        self.assertRegex(invitation_body, invitation_url_pattern)
        m = re.search(invitation_url_pattern, invitation_body)
        self.browser.get(m.group(0))
        # Since we're not logged in, we hit the invitation splash page.
        wait_for_sleep_after(lambda: self.click_element('#button-sign-in'))
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Sign In"))

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
        self.assertInNodeText("The username and/or password you specified are not correct.",
                              "form#login_form .alert-danger")

        # Test that a wrong username doesn't log us in.
        self._login(username="notme")
        self.assertInNodeText("The username and/or password you specified are not correct.",
                              "form#login_form .alert-danger")

        # Log in as a new user, log out, then log in a second time.
        # We should only get the account settings questions on the
        # first login.
        self._login()
        self.browser.get(self.url("/accounts/logout/"))
        self._login()

    def test_new_user_account_settings(self):
        # Log in as the user, who is new. Complete the account settings.
        # NOTE TODO: These tests will be replaced by a new user account settings in late summer 2021

        self._login()

        # self.click_element('#user-menu-dropdown')
        wait_for_sleep_after(lambda: self.click_element('#user-menu-dropdown'))
        wait_for_sleep_after(lambda: self.click_element('#user-menu-account-settings'))
        var_sleep(.5) # wait for page to open
        wait_for_sleep_after(lambda: self.assertIn("Account Settings", self.browser.title))

        #  # - The user is looking at the Introduction page.
        # wait_for_sleep_after(lambda: self.click_element("#save-button"))
        #  # - Now at the what is your name page?
        # wait_for_sleep_after(lambda: self.fill_field("#inputctrl", "John Doe"))
        # wait_for_sleep_after(lambda: self.click_element("#save-button"))

        # - We're on the module finished page.
        # wait_for_sleep_after(lambda: self.assertNodeNotVisible('#return-to-project'))
        # wait_for_sleep_after(lambda: self.click_element("#return-to-projects"))

        # wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Your Compliance Projects"))
        # wait_for_sleep_after(lambda: self.assertNodeNotVisible('#please-complete-account-settings'))

    def test_static_pages(self):
        self.browser.get(self.url("/privacy"))
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Privacy Policy"))

        wait_for_sleep_after(lambda: self.browser.get(self.url("/terms-of-service")))
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Terms of Service"))

        wait_for_sleep_after(lambda: self.browser.get(self.url("/love-assessments")))
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Love Assessments"))

    def test_session_timeout(self):
        self._login()
        if "Warning Message" in self.browser.title:
            self.click_element("#btn-accept")
        self.browser.get(self.url("/session_security/ping/?idleFor=0"))
        self.assertInNodeText("0", "body")

    def test_simple_module(self):
        # Log in and create a new project and start its task.
        self._login()
        self._new_project()
        task = self._start_task()

        # Answer the questions.

        # Introduction screen.
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Next Question: Module Introduction"))
        var_sleep(.5)
        wait_for_sleep_after(lambda: self.click_element("#save-button"))

        # Text question.
        wait_for_sleep_after(lambda: self.assertIn("| A Simple Module - GovReady-Q", self.browser.title))

        wait_for_sleep_after(lambda: self.fill_field("#inputctrl", "This is some text."))
        wait_for_sleep_after(lambda: self.click_element("#save-button"))

        # Finished.
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "^A Simple Module - "))

        # Go to project page, then review page.
        # self.click_element("#return-to-project")
        self.click_element("#btn-review-answers")

        # Mark the answer as reviewed then test that it was saved.
        wait_for_sleep_after(lambda: self.click_element(".task-" + str(task.id) + "-answer-q1-review-1"))

        var_sleep(.5)  # wait for ajax
        for question, answer in task.get_current_answer_records():
            if question.key == "q1":
                self.assertEqual(answer.reviewed, 1)


class AccountSettingsTests(OrganizationSiteFunctionalTests):

    def fill_in_account_settings(self, email, title, name):

        self.clear_and_fill_field("#id_name", name)
        self.clear_and_fill_field("#id_email", email)
        self.clear_and_fill_field("#id_title", title)

    def fail_fill_in_account_settings(self):
        self.clear_and_fill_field('#id_name', "")

    def test_account_settings(self):
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/account/settings"))
        self.assertEqual(urlparse(self.browser.current_url).path, "/account/settings")
        self.fill_in_account_settings(email="tester@aol.com", name="Mr.Dude", title="Account_tester")
        self.click_element("#edit_account_submit")

    def test_name_fail_account_settings(self):
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/account/settings"))
        self.fill_in_account_settings(email="tester@govready.com", name="", title="Account_tester")
        self.click_element("#edit_account_submit")
        wait_for_sleep_after(lambda: self.assertInNodeText("Display name None not available.", ".has-error"))

    def test_email_fail_account_settings(self):
        # test for duplicate email name
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/account/settings"))
        self.fill_in_account_settings(email="", name="Test_Name", title="Account_tester")
        self.click_element("#edit_account_submit")
        wait_for_sleep_after(lambda: self.assertInNodeText("Email not available.", ".has-error"))

    def test_account_settings_name_is_required(self):
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/account/settings"))
        self.assertEqual(urlparse(self.browser.current_url).path, "/account/settings")
        self.assertIn("Account Settings", self.browser.title, 'String: "Account Settings" not included in browser title')
        self.fill_in_account_settings(email="tester@aol.com", name="Dude Guy Man", title="Account_tester")
        self.click_element("#edit_account_submit")


class QuestionsTests(OrganizationSiteFunctionalTests):

    def _test_api_get(self, path, expected_value):
        resp = self.client_get(
            "/api/v1/projects/" + str(self.current_project.id) + "/answers",
            HTTP_AUTHORIZATION=self.user.api_key_rw)
        resp = resp.json()
        self.assertTrue(isinstance(resp, dict))
        self.assertEqual(resp.get("schema"), "GovReady Q Project API 1.0")
        for p in ["project"] + path:
            self.assertTrue(isinstance(resp, dict))
            self.assertIn(p, resp)
            resp = resp[p]
        self.assertEqual(resp, expected_value)
        var_sleep(1)

    @unittest.skip
    def test_questions_text(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        wait_for_sleep_after(lambda: self.click_element('#question-question_types_text'))

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Module Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # Click interstitial "Got it" button
        wait_for_sleep_after(lambda: self.click_element("#save-button"))
        var_sleep(1)

        # text
        wait_for_sleep_after(
            lambda: self.assertIn("| Test The Text Input Question Types - GovReady-Q", self.browser.title))
        wait_for_sleep_after(lambda: self.fill_field("#inputctrl", "This is some text."))
        self.click_element("#save-button")
        var_sleep(.5)
        wait_for_sleep_after(lambda: self._test_api_get(["question_types_text", "q_text"], "This is some text."))

        # text w/ default
        self.assertRegex(self.browser.title, "Next Question: text_with_default")
        self.click_element("#save-button")
        var_sleep(.5)
        wait_for_sleep_after(lambda: self._test_api_get(["question_types_text", "q_text_with_default"], "I am a kiwi."))

        # password-type question input (this is not a user pwd)
        self.assertRegex(self.browser.title, "Next Question: password")
        self.fill_field("#inputctrl", "th1s1z@p@ssw0rd!")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_password"], "th1s1z@p@ssw0rd!")

        # email-address
        self.assertRegex(self.browser.title, "Next Question: email-address")

        # test a bad address
        self.fill_field("#inputctrl", "a@a")
        self.click_element("#save-button")
        wait_for_sleep_after(
            lambda: self.assertInNodeText("is not valid.", "#global_modal p"))  # make sure we get a stern message.
        wait_for_sleep_after(lambda: self.click_element("#global_modal button"))  # dismiss the warning.
        var_sleep(.5)

        # test a good address
        val = "test+%s@q.govready.com" % get_random_string(8)
        wait_for_sleep_after(lambda: self.clear_and_fill_field("#inputctrl", val))
        self.click_element("#save-button")
        var_sleep(.5)
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
        self._test_api_get(["question_types_text", "q_longtext"],
                           'This is a paragraph\\.\n\n\n\nThis is another paragraph\\.')
        self._test_api_get(["question_types_text", "q_longtext.html"],
                           "<p>This is a paragraph.</p>\n<p>This is another paragraph.</p>")

        # longtext w/ default
        self.assertRegex(self.browser.title, "Next Question: longtext_with_default")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_longtext_with_default"],
                           "Peaches are sweet\\.\n\nThat\\'s why I write two paragraphs about peaches\\.")
        self._test_api_get(["question_types_text", "q_longtext_with_default.html"],
                           "<p>Peaches are sweet.</p>\n<p>That's why I write two paragraphs about peaches.</p>")

        # date
        self.assertRegex(self.browser.title, "Next Question: date")

        # test a bad date
        self.select_option("select[name='value_year']", "2016")
        self.select_option("select[name='value_month']", "2")
        self.select_option("select[name='value_day']", "31")
        self.click_element("#save-button")

        wait_for_sleep_after(lambda: self.assertInNodeText("day is out of range for month",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # test a good date
        self.select_option("select[name='value_year']", "2016")
        self.select_option("select[name='value_month']", "8")
        self.select_option("select[name='value_day']", "22")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_date"], "2016-08-22")  # make sure we get a stern message.

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Text Input Question Types - ")
        # Need new tests for testing text appeared in linked output document instead of on the finished page as we use to test below
        # self.assertInNodeText("I am a kiwi.", "#document-1-body") # text default should appear
        # self.assertInNodeText("Peaches are sweet.", "#document-1-body") # text default should appear
    @unittest.skip
    def test_questions_choice(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_choice')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Module Introduction")
        wait_for_sleep_after(lambda: self.click_element("#save-button"))
        var_sleep(.5)

        # Click interstitial "Got it" button
        wait_for_sleep_after(lambda: self.click_element("#save-button"))
        var_sleep(.5)

        # choice
        self.assertIn("| Test The Choice Question Types - GovReady-Q", self.browser.title)
        self.click_element('#question input[name="value"][value="choice2"]')
        self.click_element("#save-button")
        var_sleep(1.5)

        wait_for_sleep_after(lambda: self._test_api_get(["question_types_choice", "q_choice"], "choice2"))
        self._test_api_get(["question_types_choice", "q_choice.text"], "Choice 2")
        var_sleep(1)

        # yesno
        self.assertRegex(self.browser.title, "Next Question: yesno")
        self.click_element('#question input[name="value"][value="yes"]')
        self.click_element("#save-button")
        var_sleep(1)
        wait_for_sleep_after(lambda: self._test_api_get(["question_types_choice", "q_yesno"], "yes"))
        self._test_api_get(["question_types_choice", "q_yesno.text"], "Yes")

        # multiple-choice
        self.assertRegex(self.browser.title, "Next Question: multiple-choice")
        self.click_element('#question input[name="value"][value="choice1"]')
        self.click_element('#question input[name="value"][value="choice3"]')
        self.click_element("#save-button")
        var_sleep(1)
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
    @unittest.skip
    def test_questions_numeric(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_numeric')

        # Introduction screen.
        var_sleep(0.75)
        self.assertRegex(self.browser.title, "Next Question: Module Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # integer
        self.assertIn("| Test The Numeric Question Types - GovReady-Q", self.browser.title)

        # Click interstitial "Got it" button
        self.click_element("#save-button")
        var_sleep(1)

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(1.5)

        wait_for_sleep_after(lambda: self.assertInNodeText("Invalid input. Must be a whole number.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a string.
        self.clear_and_fill_field("#inputctrl", "asdf")
        self.click_element("#save-button")

        # This is caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.
        wait_for_sleep_after(
            lambda: self.assertIn("| Test The Numeric Question Types - GovReady-Q", self.browser.title))

        # Test a good integer.
        wait_for_sleep_after(lambda: self.clear_and_fill_field("#inputctrl", "5000"))
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_integer"], 5000)

        # integer min/max
        self.assertRegex(self.browser.title, "Next Question: integer min/max")

        # Test a too-small number
        self.clear_and_fill_field("#inputctrl", "0")
        self.click_element("#save-button")

        wait_for_sleep_after(lambda: self.assertInNodeText("Must be at least 1.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a too-large number
        self.clear_and_fill_field("#inputctrl", "27")
        self.click_element("#save-button")

        wait_for_sleep_after(lambda: self.assertInNodeText("Must be at most 10.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(.5)

        # This should be caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.

        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Next Question: integer min/max"))

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

        wait_for_sleep_after(lambda: self.assertInNodeText("Must be at least 1.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a too-large number
        self.clear_and_fill_field("#inputctrl", "15000")
        self.click_element("#save-button")

        wait_for_sleep_after(lambda: self.assertInNodeText("Must be at most 10000.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")

        wait_for_sleep_after(lambda: self.assertInNodeText("Invalid input. Must be a whole number.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

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
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "Next Question: real"))

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

        wait_for_sleep_after(lambda: self.assertInNodeText("Must be at least 1.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a number that's too large.
        self.clear_and_fill_field("#inputctrl", "1000")
        self.click_element("#save-button")

        wait_for_sleep_after(lambda: self.assertInNodeText("Must be at most 100.",
                                                           "#global_modal p"))  # make sure we get a stern message.
        self.click_element("#global_modal button")  # dismiss the warning.

        # Test a real number.
        self.clear_and_fill_field("#inputctrl", "23.051")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_numeric", "q_real_minmax"], 23.051)

        # Finished.
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "^Test The Numeric Question Types - "))
    @unittest.skip
    def test_questions_media(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_media')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Module Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # file upload
        wait_for_sleep_after(lambda: self.assertIn("| Test The Media Question Types - GovReady-Q", self.browser.title))

        # Click interstitial "Got it" button
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

        self.click_element("#save-button")
        var_sleep(1)

        self.assertRegex(self.browser.title, "^Test The Media Question Types - ")
        self.assertInNodeText("Download attachment (image; 90.5 kB; ", ".output-document div[data-question='file']")
    @unittest.skip
    def test_questions_module(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        # start "Test The Module Question Types"
        self.click_element('#question-question_types_module')
        var_sleep(1.5)

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Module Introduction")
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
            print("change_answer() - self.click_element(\"#link-to-question-q_module a\")")  # debug
            self.click_element("#link-to-question-q_module a")
            var_sleep(3)

        change_answer()
        self.assertIn("| Test The Module Question Types - GovReady-Q", self.browser.title)
        self.click_element('#question input[name="value"][value="__new"]')
        var_sleep(1)
        # Next button
        self.click_element("#save-button")
        var_sleep(1)

        # Got it button
        self.click_element("#save-button")
        var_sleep(1)

        # Click module and then select start over
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
        self._login()
        # test navigating to settings page not logged in
        self.browser.get(self.url("/settings"))
        self.assertRegex(self.browser.title, "GovReady-Q")
        self.assertNotRegex(self.browser.title, "GovReady Setup")
        var_sleep(0.5)

        # login as user without admin privileges and test settings page unreachable
        wait_for_sleep_after(lambda: self.browser.get(self.url("/accounts/logout/")))
        self._login(self.user2.username, self.user2.clear_password)
        if "Warning Message" in self.browser.title:
            self.click_element("#btn-accept")
        self.browser.get(self.url("/projects"))
        var_sleep(1)

        self.browser.get(self.url("/settings"))
        self.assertInNodeText("You do not have access to this page.", "body")

        # logout
        self.browser.get(self.url("/accounts/logout/"))

        # login as user with admin privileges access settings page
        self._login()
        self.browser.get(self.url("/settings"))
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title, "GovReady-Q Setup"))

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


class ProjectTests(TestCaseWithFixtureData):
    """
    Test various project views
    """

    def setUp(self):
        super().setUp()
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_project_edit(self):
        """
        Testing the edit of a project title, version, version comment, and compliance app version.
        """

        self.assertEqual(self.project.title, 'I want to answer some questions on Q.')
        self.assertEqual(self.project.version, "1.0")
        self.assertEqual(self.project.version_comment, None)

        proj_id = self.project.id
        element = Element()
        element.name = self.project.title
        element.element_type = "system"
        element.save()
        # Create system
        system = System(root_element=element)
        system.save()
        # Link system to project
        self.project.system = system
        self.project.save()

        request_body = {'project_title': ['Test Project v2'],
                        'project_version': ['1.1'], 'project_version_comment': ['A new comment!']}

        post_request = self.factory.post(f'/projects/{proj_id}/__edit', request_body)
        response = project_edit(post_request, proj_id)
        self.assertEqual(response.status_code, 302)

        # The now updated project
        edit_project = Project.objects.get(id=proj_id)
        self.assertEqual(edit_project.title, 'Test Project v2')
        self.assertEqual(edit_project.version, "1.1")
        self.assertEqual(edit_project.version_comment, "A new comment!")


