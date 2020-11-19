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

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from .oscal import Catalogs, Catalog
from .models import *
from siteapp.models import User

# from controls.oscal import Catalogs, Catalog

# ####### siteapp.test
# import os
# import os.path
# import re
# from unittest import skip

# from django.conf import settings
# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from django.utils.crypto import get_random_string

# from siteapp.models import (Organization, Portfolio, Project,
#                             ProjectMembership, User)

# ######guidedmodules.test
# from django.test import TestCase
# from django.conf import settings

# from siteapp.models import Organization, Project, User
# from guidedmodules.models import Module, Task, TaskAnswer
# from guidedmodules.module_logic import *
# from guidedmodules.app_loading import load_app_into_database


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
        settings.ALLOWED_HOSTS = ['localhost', 'testserver']
        settings.SITE_ROOT_URL = cls.live_server_url

        # In order for these tests to succeed when not connected to the
        # Internet, disable email deliverability checks which query DNS.
        settings.VALIDATE_EMAIL_DELIVERABILITY = False

        ## Turn on DEBUG so we can see errors better.
        #settings.DEBUG = True

        # Start a headless browser.
        import selenium.webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = selenium.webdriver.ChromeOptions()
        options.add_argument("disable-infobars") # "Chrome is being controlled by automated test software."
        if SeleniumTest.window_geometry == "maximized":
            options.add_argument("start-maximized") # too small screens make clicking some things difficult
        else:
            options.add_argument("--window-size=" + ",".join(str(dim) for dim in SeleniumTest.window_geometry))
        options.add_argument("--incognito")
        cls.browser = selenium.webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)
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

#####################################################################

# Control Tests

class SampleTest(TestCase):
    ## Simply dummy test ##
    def test_tests(self):
        self.assertEqual(1,1)

class Oscal80053Tests(TestCase):
    # Test
    def test_catalog_load_control(self):
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['au-2']
        self.assertEqual(control['id'].upper(), "AU-2")
        # self.assertEqual(control.class, "NIST.800.53")
        # TODO: ADD Class into object
        self.assertEqual(control['title'].upper(), "AUDIT EVENTS")

    def test_catalog_all_controls_with_organizational_parameters(self):
        parameter_values = { 'ac-1_prm_2': 'every 12 parsecs' }
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4, 
                                 parameter_values=parameter_values)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['ac-1']
        description = control['description']
        self.assertTrue('every 12 parsecs' in description, description)

    def test_catalog_one_control_with_organizational_parameters(self):
        parameter_values = { 'ac-1_prm_2': 'every 12 parsecs' }
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4,
                                 parameter_values=parameter_values)
        control = cg.get_control_by_id('ac-1')
        flat = cg.get_flattened_control_as_dict(control)
        description = flat['description']
        self.assertTrue('every 12 parsecs' in description, description)

    def test_catalog_control_organization_parameters_hashing(self):
        # no org params
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['ac-1']
        description = control['description']
        self.assertTrue('Access control policy [organization-defined frequency]' in description,
                        description)

        # set org params
        parameter_values_1 = { 'ac-1_prm_2': 'every 12 parsecs' }
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4, parameter_values=parameter_values_1)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['ac-1']
        description = control['description']
        self.assertTrue('Access control policy every 12 parsecs' in description,
                        description)

        # different org params, we should get back a different instance
        parameter_values_2 = { 'ac-1_prm_2': 'every 13 parsecs' }
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4, parameter_values=parameter_values_2)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['ac-1']
        description = control['description']
        self.assertTrue('Access control policy every 13 parsecs' in description,
                        description)

        # switch back to prev org params, we should get an appropriate instance
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4, parameter_values=parameter_values_1)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['ac-1']
        description = control['description']
        self.assertTrue('Access control policy every 12 parsecs' in description,
                        description)

        

#####################################################################

class ControlUITests(SeleniumTest):
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

# class ControlUIControlEditorTests(SeleniumTest):
#     def test_homepage(self):
#         self.browser.get(self.url("/controls/editor"))
#         self.assertInNodeText("Test works", "p")

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
            sid = "au-3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is a test statement.",
            statement_type = "control",
            status = "Implemented"
        )
        self.assertIsNotNone(smt.id)
        self.assertEqual(smt.status, "Implemented")
        self.assertEqual(smt.sid, "au-3")
        self.assertEqual(smt.body, "This is a test statement.")
        self.assertEqual(smt.sid_class, "NIST_SP-800-53_rev4")
        # Test updating status and retrieving statement
        smt.status = "Partially Implemented"
        smt.save()
        smt2 = Statement.objects.get(pk=smt.id)
        self.assertEqual(smt2.sid, "au-3")
        self.assertEqual(smt2.status, "Partially Implemented")

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



