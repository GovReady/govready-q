# This module tests integrations between projects and systems.
# This is a separate file because the tests cut across modules.

import os
import os.path
import re
from unittest import skip

from django.conf import settings
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.crypto import get_random_string
from guardian.shortcuts import (assign_perm, get_objects_for_user,
                                get_perms_for_model, get_user_perms,
                                get_users_with_perms, remove_perm)

from siteapp.models import (Organization, Portfolio, Project,
                            ProjectMembership, User)

from controls.oscal import Catalogs, Catalog
from controls.models import *
from .tests import var_sleep, SeleniumTest


class ProjectSystemPermissionsUnitTests(SeleniumTest):

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

    def test_project_system_element_permission_non_admin_user(self):
        """Test non-admin user inviting another non-admin correctly assigns project, system and root_element permissions
           This only tests assignments, does not test experience in interface."""

        # Create non-admin users nau1, nau2
        self.nau1 = User.objects.create(username="non-admin-user-1", email="nau1@example.com")
        self.nau1.clear_password = get_random_string(16)
        self.nau1.set_password(self.nau1.clear_password)
        self.nau1.save()

        self.nau2 = User.objects.create(username="non-admin-user-2", email="nau2@example.com")
        self.nau2.clear_password = get_random_string(16)
        self.nau2.set_password(self.nau2.clear_password)
        self.nau2.save()

        # Login in nau1
        self._login(username=self.nau1.username, password=self.nau1.clear_password)

        # nau1 starts a project
        p = Project.objects.create()
        p.save()
        e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Element")
        self.assertTrue(e.full_name == "New Element Full Name")
        self.assertTrue(e.element_type == "system")
        s = System(root_element=e)
        s.save()
        p.system = s
        p.save()

        p.assign_edit_permissions(self.nau1)
        s.assign_edit_permissions(self.nau1)

        # nau2 invites nau2 to the project
        # request.POST.get("user_id")

        send_invitation_data = {'project':p.id,
                                'user_id':self.nau2.id
                                }
        # send POST request.
        # url(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
        # response = self.client.post(path='/invitation/_send', data=send_invitation_data)

        # print("response", response)
        # from pprint import pprint
        # print("response.__dict__", pprint(response.__dict__))
        # print("response.message", response.message)

        # Test if nau2 has proper permissions on project, system, root_element
        # e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        # self.assertTrue(e.id is not None)
        # self.assertTrue(e.name == "New Element")
        # self.assertTrue(e.full_name == "New Element Full Name")
        # self.assertTrue(e.element_type == "system")
        # s = System(root_element=e)
        # s.save()
        # self.assertEqual(s.root_element.name,e.name)

        # u2 = User.objects.create(username="Jane2", email="jane@example.com")
        # # Test no permissions for user
        # perms = get_user_perms(u2, s)
        # self.assertTrue(len(perms) == 0)

        # # Assign owner permissions
        # s.assign_owner_permissions(u2)
        # perms = get_user_perms(u2, s)
        # self.assertTrue(len(perms) == 4)
        # self.assertIn('add_system', perms)
        # self.assertIn('change_system', perms)
        # self.assertIn('delete_system', perms)
        # self.assertIn('view_system', perms)

class StatementUITests(SeleniumTest):

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

    def test_homepage(self):
        self.browser.get(self.url("/controls/"))

    def test_statement_updates(self):
        # Create non-admin users nau3
        self.nau3 = User.objects.create(username="non-admin-user-3", email="nau3@example.com")
        self.nau3.clear_password = get_random_string(16)
        self.nau3.set_password(self.nau3.clear_password)
        print("username/pw", self.nau3.username, self.nau3.clear_password)
        self.nau3.save()
        # Make user admin to explore objects
        # self.nau3.is_superuser = True
        # self.nau3.is_staff = True
        # self.nau3.is_admin = True
        # self.nau3.save()

        # Login in nau3
        self._login(username=self.nau3.username, password=self.nau3.clear_password)

        # nau3 starts a project
        p = Project.objects.create()
        p.save()
        # Create a root element for system
        e = Element.objects.create(name="New Root Element", full_name="New Root Element Full Name", element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Root Element")
        self.assertTrue(e.full_name == "New Root Element Full Name")
        self.assertTrue(e.element_type == "system")
        s = System(root_element=e)
        s.save()
        p.system = s
        p.save()

        p.assign_edit_permissions(self.nau3)
        s.assign_edit_permissions(self.nau3)

        # Create a producer component/element for system
        pe = Element.objects.create(name="Producer Element", full_name="New Producer Element Full Name", element_type="component")

        # Create a smt for the system
        smt = Statement.objects.create(
            sid = "au.3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is a test statement.",
            statement_type = "control",
            status = "Implemented",
            producer_element = pe,
            consumer_element = e
        )
        self.assertIsNotNone(smt.id)
        self.assertEqual(smt.status, "Implemented")
        self.assertEqual(smt.sid, "au.3")
        self.assertEqual(smt.body, "This is a test statement.")
        self.assertEqual(smt.sid_class, "NIST_SP-800-53_rev4")
        # Test updating status and retrieving statement
        smt.status = "Partially Implemented"
        smt.save()
        smt2 = Statement.objects.get(pk=smt.id)
        self.assertEqual(smt.sid, "au.3")
        self.assertEqual(smt.status, "Partially Implemented")

        # Update statement
        smt.status = "This is a test statement that has now been updated."
        # Check page exists
        print("Testing URL: ", self.url("/systems/{}/controls/updated".format(s.id)))
        self.browser.get(self.url("/systems/{}/controls/updated".format(s.id)))
        var_sleep(0.4)
        self.assertRegex(self.browser.title, "Controls Updated")
