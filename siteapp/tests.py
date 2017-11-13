from django.conf import settings
from django.test import SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from unittest import skip

import os
import random
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
        settings.ALLOWED_HOSTS = ['.localhost', 'testserver']
        settings.SITE_ROOT_URL = cls.live_server_url
        settings.ORGANIZATION_PARENT_DOMAIN = 'orgs.localhost'

        ## Turn on DEBUG so we can see errors better.
        #settings.DEBUG = True

        # Start a headless browser.
        import selenium.webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        os.environ['PATH'] += ":/usr/lib/chromium-browser" # 'chromedriver' executable needs to be in PATH (for newer Ubuntu)
        os.environ['PATH'] += ":/usr/lib/chromium" # 'chromedriver' executable needs to be in PATH (for Debian 8)
        options = selenium.webdriver.ChromeOptions()
        options.add_argument("disable-infobars") # "Chrome is being controlled by automated test software."
        options.add_argument("start-maximized") # too small screens make clicking some things difficult
        options.add_argument("--incognito")
        cls.browser = selenium.webdriver.Chrome(chrome_options=options)
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

    def clear_field(self, css_selector):
        self.browser.find_element_by_css_selector(css_selector).clear()

    def fill_field(self, css_selector, text):
        self.browser.find_element_by_css_selector(css_selector).send_keys(text)

    def clear_and_fill_field(self, css_selector, text):
        self.clear_field(css_selector)
        self.fill_field(css_selector, text)

    def click_element(self, css_selector):
        # ensure element is on screen or else it can't be clicked
        # see https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView
        elem = self.browser.find_element_by_css_selector(css_selector)
        self.browser.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });", elem)
        elem.click()

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
        from guidedmodules.models import AppSource
        from guidedmodules.management.commands.load_modules import Command as load_modules
        AppSource.objects.all().delete()
        AppSource.objects.get_or_create(
              # this one exists on first db load because it's created by
              # migrations, but because the testing framework seems to
              # get rid of it after the first test in this class 
            namespace="system",
            defaults={
                "spec": { # required system projects
                    "type": "local",
                    "path": "fixtures/modules/system",
                }
            }
        )
        AppSource.objects.create(
            namespace="project",
            spec={ # contains a test project
                "type": "local",
                "path": "fixtures/modules/other",
            },
            trust_assets=True
        )
        load_modules().handle()

        # Create a default user that is a member of the organization.
        # Log the user into the test client.
        from siteapp.models import User, ProjectMembership
        self.user = User.objects.create(username="me")
        self.user.set_password("1234")
        self.user.save()
        self.user.reset_api_keys()
        self.client.login(username="me", password="1234")

        # Create the Organization.
        from siteapp.models import Organization
        self.org = Organization.create(name="Our Organization", subdomain="testorg",
            admin_user=self.user)

    def client_get(self, *args, domain=None, **kwargs):
        # Wrap the Django test client's get/post functions that sets the HTTP
        # Host: header so that the request gets to the organization site.
        assert domain in ("LANDING", "ORG")
        if domain == "LANDING":
            host = settings.LANDING_DOMAIN
        else:
            host = self.org.subdomain + "." + settings.ORGANIZATION_PARENT_DOMAIN
        resp = self.client.get(
            *args,
            **kwargs,
            HTTP_HOST=host)
        self.assertEqual(resp.status_code, 200, msg=repr(resp))
        return resp # .content.decode("utf8")

    def url(self, path):
        # Within this test, we only generate URLs for the organization subdomain.
        return super().url(self.org.subdomain, path)

    def _login(self, username="me", password="1234"):
        # Fill in the login form and submit.
        self.browser.get(self.url("/"))

        self.assertRegex(self.browser.title, "Home")
        self.fill_field("#id_login", username)
        self.fill_field("#id_password", password)
        self.click_element("form button.primaryAction")

    def _new_project(self, module_key="project/simple_project"):
        self.browser.get(self.url("/projects"))
        self.click_element("#new-project")
        self.click_element(".app[data-app='%s']" % module_key)
        self.click_element("#start-project")
        self.click_element("#start-project")
        var_sleep(1)
        self.assertRegex(self.browser.title, "I want to answer some questions on Q.")

        from siteapp.models import Project
        m = re.match(r"http://.*?/projects/(\d+)/", self.browser.current_url)
        self.current_projet = Project.objects.get(id=m.group(1))

    def _start_task(self):
        # Assumes _new_project() just finished.

        # Start the task.
        self.click_element('#question-simple_module')

class GeneralTests(OrganizationSiteFunctionalTests):

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

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "GovReady Q")

    def test_login(self):
        # Test that a wrong password doesn't log us in.
        self._login(password="badpw")
        self.assertInNodeText("The username and/or password you specified are not correct.", "form.login .alert-danger")

        # Test that a wrong username doesn't log us in.
        self._login(username="notme")
        self.assertInNodeText("The username and/or password you specified are not correct.", "form.login .alert-danger")

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
        self.assertRegex(self.browser.title, "Project Folders")
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

        def start_invitation(email):
            # Fill out the invitation modal.
            var_sleep(.5) # wait for modal to show

            # in case there are other team members and the select box is showing,
            # choose
            self.select_option('#invite-user-select', '__invite__')

            self.fill_field("#invitation_modal #invite-user-email", email)
            self.click_element("#invitation_modal button.btn-submit")

        def do_invitation(email):
            start_invitation(email)

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

        # Test an invitation to that project. For unknown reasons, when
        # executing this on CircleCI (but not locally), the click fails
        # because the element is not clickable -- it reports a coordinate
        # that's above the button in the site header. Not sure what's
        # happening. So load the modal using Javascript.
        #self.click_element("#show-project-invite")
        self.browser.execute_script("invite_user_into_project()")
        var_sleep(.5) # modal fades in

        # Test an invalid email address.
        start_invitation("example")
        var_sleep(.5)
        self.assertInNodeText("The email address is not valid.", "#global_modal") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)
        #self.click_element("#show-project-invite") # Re-open the invite box.
        self.browser.execute_script("invite_user_into_project()") # See comment above.

        do_invitation("test+project@q.govready.com")
        self.assertRegex(self.browser.title, "I want to answer some questions on Q") # user is on the project page
        self.click_element('#question-simple_module') # go to the task page
        self.assertRegex(self.browser.title, "A Simple Module") # user is on the task page

        reset_login()

        # Test an invitation to take over editing a task but without joining the project.
        self.click_element('#question-simple_module') # go to the task page
        var_sleep(.5) # wait for page to load
        self.click_element("#save-button") # pass over the Introductory question because the Help link is suppressed on interstitials
        var_sleep(.5) # wait for page to load
        self.click_element('#transfer-editorship a')
        do_invitation("test+editor@q.govready.com")
        var_sleep(5)
        self.assertRegex(self.browser.title, "A Simple Module") # user is on the task page

        reset_login()

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
        self.fill_field("#discussion-your-comment .ql-editor", "Hello is anyone *here*?")
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
        self.fill_field("#discussion-your-comment .ql-editor", "Yes, @me, I am here!\n\nI am here with you!")
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

        # Log back in as the original user.
        discussion_page = self.browser.current_url
        self.browser.get(self.url("/accounts/logout/"))
        self._login()
        self.browser.get(discussion_page)

        # Test that we can see the comment and the reaction.
        self.assertInNodeText("Yes, @me, I am here", "#discussion .comment:not(.author-is-self) .comment-text")
        self.assertInNodeText("reacted", "#discussion .replies .reply[data-emojis=heart]")

class QuestionsTests(OrganizationSiteFunctionalTests):

    def _test_api_get(self, path, expected_value):
        resp = self.client_get(
                "/api/v1/organizations/" + self.org.subdomain + "/projects/" + str(self.current_projet.id) + "/answers",
                domain="LANDING",
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
        self._login()
        self._new_project()
        self.click_element('#question-question_types_text')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # text
        self.assertRegex(self.browser.title, "Next Question: text")
        self.fill_field("#inputctrl", "This is some text.")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_text"], "This is some text.")

        # text w/ default
        self.assertRegex(self.browser.title, "Next Question: text_with_default")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_text_with_default"], "I am a kiwi.")

        # password
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
        var_sleep(.5)
        self.assertInNodeText("is not valid.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

        # test a good address
        val = "test+%d@q.govready.com" % random.randint(10000, 99999)
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
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_longtext"], 'This is a paragraph\\.\r\n\r\n\r\n\r\nThis is another paragraph\\.')
        self._test_api_get(["question_types_text", "q_longtext.html"], "<p>This is a paragraph.</p>\n<p>This is another paragraph.</p>")

        # longtext w/ default
        self.assertRegex(self.browser.title, "Next Question: longtext_with_default")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_longtext_with_default"], "Peaches are sweet\\.\r\n\r\nThat\\'s why I write two paragraphs about peaches\\.")
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
        var_sleep(.5)

        # test a good date
        self.select_option("select[name='value_year']", "2016")
        self.select_option("select[name='value_month']", "8")
        self.select_option("select[name='value_day']", "22")
        self.click_element("#save-button")
        var_sleep(.5)
        self._test_api_get(["question_types_text", "q_date"], "2016-08-22")

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Text Input Question Types - ")
        self.assertInNodeText("I am a kiwi.", "#document-1-body") # text default should appear
        self.assertInNodeText("Peaches are sweet.", "#document-1-body") # text default should appear

    def test_questions_choice(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_choice')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # choice
        self.assertRegex(self.browser.title, "Next Question: choice")
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

        # Finished.
        self.assertRegex(self.browser.title, "^Test The Choice Question Types - ")

    def test_questions_numeric(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_numeric')

        # Introduction screen.
        self.assertRegex(self.browser.title, "Next Question: Introduction")
        self.click_element("#save-button")
        var_sleep(.5)

        # integer
        self.assertRegex(self.browser.title, "Next Question: integer")

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Invalid input. Must be a whole number.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

        # Test a string.
        self.clear_and_fill_field("#inputctrl", "asdf")
        self.click_element("#save-button")
        var_sleep(.5)

        # This is caught by the browser itself, so we don't have to dismiss anything.
        # Make sure we haven't moved past the url page.
        self.assertRegex(self.browser.title, "Next Question: integer")
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
        var_sleep(.5)

        # Test a too-large number
        self.clear_and_fill_field("#inputctrl", "27")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at most 10.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

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
        var_sleep(.5)

        # Test a too-large number
        self.clear_and_fill_field("#inputctrl", "15000")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at most 10000.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

        # Test a non-integer.
        self.clear_and_fill_field("#inputctrl", "1.01")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Invalid input. Must be a whole number.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

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
        var_sleep(.5)

        # Test a number that's too large.
        self.clear_and_fill_field("#inputctrl", "1000")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertInNodeText("Must be at most 100.", "#global_modal p") # make sure we get a stern message.
        self.click_element("#global_modal button") # dismiss the warning.
        var_sleep(.5)

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
        self.assertRegex(self.browser.title, "Next Question: file")

        # We need to upload a file that we know exists.
        testFilePath = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fixtures',
            'testimage.png'
        )
        self.fill_field("#inputctrl", testFilePath)

        self.click_element("#save-button")
        var_sleep(1)

        # interstitial
        # nothing to really test in terms of functionality, but check that
        # page elements are present
        self.assertRegex(self.browser.title, "Next Question: interstitial")
        self.assertInNodeText("This is an interstitial.", "h1")

        self.click_element("#save-button")
        var_sleep(.5)

        # external-function
        # There is nothing to really test in terms of functionality here, but
        # the template result should show the output of the sample_external_function
        # method defined below.
        self.assertRegex(self.browser.title, "Next Question: external-function")
        self.click_element("#save-button")
        var_sleep(.5)

        self.assertRegex(self.browser.title, "^Test The Media Question Types - ")
        self.assertInNodeText("Successfully ran an external function",
        	".output-document span[data-question='external-function']")

    def test_questions_module(self):
        # Log in and create a new project.
        self._login()
        self._new_project()
        self.click_element('#question-question_types_module')

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
        self.click_element('#question-question_types_encrypted')

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
