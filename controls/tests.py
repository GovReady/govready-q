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
# import os.path
import re
from unittest import skip

from django.conf import settings
from django.test import TestCase
from django.utils.crypto import get_random_string
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from .oscal import Catalogs, Catalog
from siteapp.models import (Organization, Portfolio, Project,
                            ProjectMembership, User)
from .models import *
from siteapp.models import User

# Import SeleniumTest and OrganizationSiteFunctionalTests from siteapp to keep things DRY
from siteapp.tests import SeleniumTest, OrganizationSiteFunctionalTests

def var_sleep(duration):
    '''
    Tweak sleep globally by multple, a fraction, or depend on env
    '''
    from time import sleep
    sleep(duration*2)


class SampleTest(TestCase):
    ## Simply dummy test ##
    def test_tests(self):
        self.assertEqual(1,1)

class Oscal80053Tests(TestCase):
    # Test 
    def test_catalog_load_control(self):
        cg = Catalog.GetInstance('NIST_SP-800-53_rev4')
        cg_flat = cg.get_flattended_controls_all_as_dict()
        control = cg_flat['au-2']
        self.assertEqual(control['id'].upper(), "AU-2")
        # self.assertEqual(control.class, "NIST.800.53")
        # TODO: ADD Class into object
        self.assertEqual(control['title'].upper(), "AUDIT EVENTS")

#####################################################################

class GeneralTests(OrganizationSiteFunctionalTests):

    def test_homepage(self):
        self.browser.get(self.url("/"))
        self.assertRegex(self.browser.title, "Welcome to Compliance Automation")

    def test_login(self):
        # Test that a wrong password doesn't log us in.
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

class ControlUITests(OrganizationSiteFunctionalTests):
    def test_homepage(self):
        self.browser.get(self.url("/controls/"))

    def test_control_lookup(self):
        self.browser.get(self.url("/controls/catalogs/NIST_SP-800-53_rev4/control/au-2"))
        var_sleep(2)
        self.assertInNodeText("AU-2", "#control-heading")
        self.assertInNodeText("Audit Events", "#control-heading")

    def test_control_enhancement_lookup(self):
        self.browser.get(self.url("/controls/catalogs/NIST_SP-800-53_rev4/control/AC-2 (4)"))
        self.assertInNodeText("AC-2 (4)", "#control-heading")
        self.assertInNodeText("Automated Audit Actions", "#control-heading")

    # def test_control_lookup_no_matching_id(self):
    #     self.browser.get(self.url("/controls/800-53/XX-2/"))
    #     self.assertInNodeText("XX-2", "#control-heading")
    #     self.assertInNodeText("The control XX-2 was not found in the control catalog.", "#control-message")

class ControlUIControlEditorTests(OrganizationSiteFunctionalTests):
    def test_homepage(self):
        self.browser.get(self.url("/controls/editor"))
        self.assertInNodeText("Test works", "p")

    # def test_control_lookup(self):
    #     self.browser.get(self.url("/controls/800-53/AU-2/"))
    #     self.assertInNodeText("AU-2", "#control-heading")
    #     self.assertInNodeText("Audit Events", "#control-heading")

    # def test_control_enhancement_lookup(self):
    #     self.browser.get(self.url("/controls/800-53/AC-2 (4)/"))
    #     self.assertInNodeText("AC-2 (4)", "#control-heading")
    #     self.assertInNodeText("Automated Audit Actions", "#control-heading")

#####################################################################

class StatementUnitTests(TestCase):
    ## Simply dummy test ##
    def test_tests(self):
        self.assertEqual(1,1)

    def test_smt_status(self):
        # Create a smt
        smt = Statement.objects.create(
            sid = "au.3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is a test statement.",
            statement_type = "control",
            status = "Implemented"
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

    def test_control_implementation_vs_prototype(self):
        # Detection of difference in statement
        # Create a smt
        smt = Statement.objects.create(
            sid = "au.3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is a test statement.",
            statement_type = "control_implementation",
            status = "Implemented"
        )
        smt.save()
        # Create statement prototype
        smt.create_prototype()
        self.assertEqual(smt.body, smt.prototype.body)
        self.assertNotEqual(smt.id, smt.prototype.id)
        self.assertTrue(smt.prototype_synched)
        # Change statement compared to prototype
        smt.prototype.body = smt.prototype.body + "\nModified statememt"
        smt.prototype.save()
        self.assertFalse(smt.prototype_synched)
        self.assertEqual(smt.diff_prototype_main, [(0, 'This is a test statement.'), (-1, '\nModified statememt')])

class ElementUnitTests(TestCase):
    ## Simply dummy test ##
    def test_tests(self):
        self.assertEqual(1,1)

    def test_element_create(self):
        e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Element")
        self.assertTrue(e.full_name == "New Element Full Name")
        self.assertTrue(e.element_type == "system")
        e.delete()
        self.assertTrue(e.id is None)

    def test_element_assign_owner_permissions(self):
        e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        e.save()
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Element")
        # create a user
        u = User.objects.create(username="Jane", email="jane@example.com")
        # Test no permissions for user
        perms = get_user_perms(u, e)
        self.assertTrue(len(perms) == 0)

        # Assign owner permissions
        e.assign_owner_permissions(u)
        perms = get_user_perms(u, e)
        self.assertTrue(len(perms) == 4)
        self.assertIn('add_element', perms)
        self.assertIn('change_element', perms)
        self.assertIn('delete_element', perms)
        self.assertIn('view_element', perms)

class SystemUnitTests(TestCase):
    def test_system_create(self):
        e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Element")
        self.assertTrue(e.full_name == "New Element Full Name")
        self.assertTrue(e.element_type == "system")
        s = System(root_element=e)
        s.save()
        self.assertEqual(s.root_element.name,e.name)

        u2 = User.objects.create(username="Jane2", email="jane@example.com")
        # Test no permissions for user
        perms = get_user_perms(u2, s)
        self.assertTrue(len(perms) == 0)

        # Assign owner permissions
        s.assign_owner_permissions(u2)
        perms = get_user_perms(u2, s)
        self.assertTrue(len(perms) == 4)
        self.assertIn('add_system', perms)
        self.assertIn('change_system', perms)
        self.assertIn('delete_system', perms)
        self.assertIn('view_system', perms)

class PoamUnitTests(TestCase):
    """Class for Poam Unit Tests"""

    ## Simply dummy test ##
    def test_tests(self):
        self.assertEqual(1,1)

    def test_element_create(self):
        # Create a root_element and system
        e = Element.objects.create(name="New Element 2", full_name="New Element 2 Full Name", element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Element 2")
        self.assertTrue(e.full_name == "New Element 2 Full Name")
        self.assertTrue(e.element_type == "system")

        e.save()
        s = System(root_element=e)
        s.save()
        self.assertEqual(s.root_element.name,e.name)

        # Create a Poam for the system
        smt = Statement.objects.create(
            sid = None,
            sid_class = None,
            pid = None,
            body = "This is a test Poam statement.",
            statement_type = "Poam",
            status = "New",
            consumer_element = e
        )
        smt.save()
        import uuid
        poam = Poam.objects.create(statement = smt, poam_group = "New POA&M Group")
        self.assertTrue(poam.poam_group == "New POA&M Group")
        # self.assertTrue(poam.name == "New Element")
        # self.assertTrue(poam.full_name == "New Element Full Name")
        # self.assertTrue(poam.element_type == "system")
        poam.save()
        # poam.delete()
        # self.assertTrue(poam.uuid is None)



