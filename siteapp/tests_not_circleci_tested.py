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
# <<<<<<< HEAD
# from selenium.webdriver import DesiredCapabilities
# =======
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
from siteapp.tests import SeleniumTest
from siteapp.tests import OrganizationSiteFunctionalTests
from siteapp.tests import var_sleep
from siteapp.tests import wait_for_sleep_after


class GeneralTestsInvitations(OrganizationSiteFunctionalTests):

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

        def start_invitation(username):
            # Fill out the invitation modal.
            # self.select_option_by_visible_text('#invite-user-select', username) # This is for selecting user from dropdown list
            wait_for_sleep_after(lambda: self.fill_field("input#invite-user-email", username))
            wait_for_sleep_after(lambda: self.click_element("#invitation_modal button.btn-submit"))

        def do_invitation(username):
            start_invitation(username)
            var_sleep(.5)  # wait for invitation to be sent

            # Log out and accept the invitation as an anonymous user.
            self.browser.get(self.url("/accounts/logout/"))
            self._accept_invitation(username)

        def reset_login():
            # Log out and back in as the original user.
            self.browser.get(self.url("/accounts/logout/"))
            self._login()
            wait_for_sleep_after(lambda: self.browser.get(project_page))

        # Test an invitation to that project. For unknown reasons, when
        # executing this on CircleCI (but not locally), the click fails
        # because the element is not clickable -- it reports a coordinate
        # that's above the button in the site header. Not sure what's
        # happening. So load the modal using Javascript.
        wait_for_sleep_after(lambda: self.click_element("#menu-btn-show-project-invite"))
        self.browser.execute_script("invite_user_into_project()")
        # Toggle field to invite user by email
        self.browser.execute_script("$('#invite-user-email').parent().toggle(true)")

        # Test an invalid email address.
        start_invitation("example")
        wait_for_sleep_after(lambda: self.assertInNodeText("The email address is not valid.",
                                                           "#global_modal"))  # make sure we get a stern message.
        wait_for_sleep_after(lambda: self.click_element("#global_modal button"))  # dismiss the warning.

        wait_for_sleep_after(lambda: self.click_element("#menu-btn-show-project-invite"))  # Re-open the invite box.
        self.browser.execute_script("invite_user_into_project()")  # See comment above.
        # Toggle field to invite user by email

        wait_for_sleep_after(lambda: self.browser.execute_script("$('#invite-user-email').parent().toggle(true)"))
        var_sleep(3)  # Adding to avoid lock
        do_invitation(self.user2.email)
        self.fill_field("#id_login", self.user2.username)
        self.fill_field("#id_password", self.user2.clear_password)
        self.click_element("form button.primaryAction")

        self.assertRegex(self.browser.title, "I want to answer some questions on Q")  # user is on the project page
        wait_for_sleep_after(lambda: self.click_element('#question-simple_module'))  # go to the task page
        wait_for_sleep_after(lambda: self.assertRegex(self.browser.title,
                                                      "Next Question: Module Introduction"))  # user is on the task page

        # reset_login()

        # Test an invitation to take over editing a task but without joining the project.
        var_sleep(.5)
        wait_for_sleep_after(lambda: self.click_element(
            "#save-button"))  # pass over the Introductory question because the Help link is suppressed on interstitials
        wait_for_sleep_after(lambda: self.click_element('#transfer-editorship'))  # Toggle field to invite user by email

        self.browser.execute_script("$('#invite-user-email').parent().toggle(true)")
        wait_for_sleep_after(lambda: do_invitation(self.user3.email))  # Toggle field to invite user by email

        self.fill_field("#id_login", self.user3.username)
        self.fill_field("#id_password", self.user3.clear_password)
        self.click_element("form button.primaryAction")
        wait_for_sleep_after(
            lambda: self.assertRegex(self.browser.title, "Next Question: The Question"))  # user is on the task page

        # Test assigning existing user to a project.
        reset_login()
        self._new_project()
        project_page = self.browser.current_url

        # And create a new task.
        self._start_task()
        task_page = self.browser.current_url

        # But now go back to the project page.
        self.browser.get(project_page)
        wait_for_sleep_after(lambda: self.click_element("#menu-btn-show-project-invite"))

        # Select username "me3"
        wait_for_sleep_after(lambda: self.select_option_by_visible_text('#invite-user-select', "me3"))
        wait_for_sleep_after(lambda: self.click_element("#invite_submit_btn"))
        wait_for_sleep_after(lambda: self.assertInNodeText("me3 granted edit permission to project", ".alert"))

        # reset_login()

        # Invitations to join discussions are tested in test_discussion.

    # def test_discussion(self):
    # from siteapp.management.commands.send_notification_emails import Command as send_notification_emails

    # # Log in and create a new project.
    # self._login()
    # self._new_project()
    # self._start_task()

    # # Move past the introduction screen.
    # self.assertRegex(self.browser.title, "Next Question: Module Introduction")
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



