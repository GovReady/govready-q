import os
import requests

from django.utils.crypto import get_random_string
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from selenium.common.exceptions import NoSuchElementException

from discussion.validators import VALID_EXTS, validate_file_extension
from guidedmodules.models import AppSource
from guidedmodules.management.commands.load_modules import Command as load_modules
from siteapp.models import User, Organization, Portfolio
from siteapp.tests import SeleniumTest, var_sleep

from selenium.common.exceptions import NoSuchElementException
from tools.utils.linux_to_dos import convert_w

from django.contrib.auth.models import Permission
from django.utils.crypto import get_random_string
from selenium.common.exceptions import NoSuchElementException

from siteapp.models import User, Organization, Portfolio
from siteapp.tests import SeleniumTest, var_sleep


FIXTURE_DIR = "fixtures"
TEST_FILENAME = "test"
TEST_SPECIAL_FILENAME = "test,.png"

class DiscussionTests(SeleniumTest):

    def setUp(self):
        super().setUp()
        # Load modules from the fixtures directory so that we have the required
        # modules as well as a test project.

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
        # Grant user permission to view appsource
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.user.save()
        # Grant user permission to view appsource
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))

        # Create the Organization.

        _org = Organization.create(name="Our Organization", slug="testorg",
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

    def _get_browser_cookies(self):
        # Gets the browser cookies and returns them
        browser_cookies = self.browser.get_cookies()
        cookies = {}
        for browser_cookie in browser_cookies:
            cookies[browser_cookie["name"]] = browser_cookie["value"]
        return cookies

    def test_validate_file_extension(self):
        # Load test file paths
        random_ext = ".random"

        for ext, _content_type in VALID_EXTS.items():
            print("Testing file type {}".format(ext))
            test_file_name = "".join([TEST_FILENAME, ext])
            test_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                FIXTURE_DIR,
                test_file_name
            )
            test_file_contents = b''

            # Read in test file
            with open(test_path, "rb") as test_file:
                test_file_contents = test_file.read()

            # Test valid file extension, content type
            file_model = SimpleUploadedFile(
                            test_file_name,
                            test_file_contents
                        )
            is_valid = validate_file_extension(file_model)
            self.assertIsNone(is_valid)

            # Test valid file extension, unsupported type
            file_model = SimpleUploadedFile(
                            test_file_name,
                            b'\x7f\x45\x4c\x46\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        )
            is_valid = validate_file_extension(file_model)
            self.assertIsNotNone(is_valid)

            # Test invalid file extension, but valid content type
            file_model = SimpleUploadedFile(
                            "".join([test_file_name, random_ext]),
                            test_file_contents
                        )
            is_valid = validate_file_extension(file_model)
            self.assertIsNotNone(is_valid)

            # Test file extension not in defined valid extensions
            file_model = SimpleUploadedFile(
                            test_file_name,
                            test_file_contents
                        )
            _file, file_ext = os.path.splitext(test_file_name)
            content_types = VALID_EXTS[file_ext] # Save original content type
            VALID_EXTS[file_ext] = [] # Mock out list of valid content types
            is_valid = validate_file_extension(file_model)
            self.assertIsNotNone(is_valid)

            # Restore list of valid content types
            VALID_EXTS[file_ext] = content_types

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
        var_sleep(1)
        self.fill_field("#discussion-your-comment", "Hello is anyone *here*?")
        var_sleep(.5)
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(.5)

        # Test Script injection
        script = "<script id='injectiontest2'>document.getElementsByTagName('body')[0]" \
                 ".appendChild('<div id=\\'injectiontest1\\'></div>');</script>"
        self.fill_field("#discussion-your-comment", script)
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

        # Test file attachments upload successfully

        # We need to upload a file that we know exists.
        test_file_name = "".join([TEST_FILENAME, ".png"])
        test_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            FIXTURE_DIR,
            test_file_name
        )

        self.filepath_conversion("#discussion-attach-file", test_file_path, "fill")

        var_sleep(.5)
        self.click_element("#discussion .comment-input button.btn-primary")

        var_sleep(.5)# Give time for the image to upload.
        # Test that we have an image.
        img = self.browser.find_element_by_css_selector('.comment[data-id="4"] .comment-text p img')
        self.assertIsNotNone(img)

        # Test that valid PNG image actually exists with valid content type.
        image_url = img.get_attribute('src')
        cookies = self._get_browser_cookies()
        response = requests.get(image_url, cookies=cookies)
        image_contents = response.content

        file_model = SimpleUploadedFile(test_file_name, image_contents, content_type="image/png")
        image_file_valid = validate_file_extension(file_model)
        self.assertIsNone(image_file_valid)

        result = self.browser.execute_script("""var http = new XMLHttpRequest();
            http.open('HEAD', '{}', false);
            http.send();
            return http.status!=404;""".format(image_url))

        self.assertTrue(result)

        # Test that we can upload files of the same name

        test_file_name = "".join([TEST_FILENAME, ".png"])
        test_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            FIXTURE_DIR,
            test_file_name
        )
        on_disk_contents = None
        with open(test_file_path, "rb") as filep:
            on_disk_contents = filep.read()

        self.filepath_conversion("#discussion-attach-file", test_file_path, "fill")

        var_sleep(1)
        self.click_element("#discussion .comment-input button.btn-primary")
        var_sleep(1)  # Give time for the image to upload.

        # Test that we still have an image.
        img = self.browser.find_element_by_css_selector('.comment[data-id="5"] .comment-text p img')
        self.assertIsNotNone(img)

        # Getting content at url
        image_url = img.get_attribute('src')
        cookies = self._get_browser_cookies()
        response = requests.get(image_url, cookies=cookies)
        image_contents = response.content

        # Test that file is the same as on disk contents
        self.assertEqual(image_contents, on_disk_contents)

        # Test that image is at attachment #2
        self.assertIn("attachment/2", image_url)


        result = self.browser.execute_script("""var http = new XMLHttpRequest();
            http.open('HEAD', '{}', false);
            http.send();
            return http.status!=404;""".format(image_url))

        self.assertTrue(result)