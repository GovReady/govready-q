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

import json
import os
from pathlib import PurePath
import re
from unittest import skip

from django.test import TestCase
from selenium.webdriver.support.select import Select
from siteapp.models import User
from siteapp.tests import SeleniumTest, OrganizationSiteFunctionalTests, var_sleep
from .models import *
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.text import slugify
from .oscal import Catalogs, Catalog
from system_settings.models import SystemSettings

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


from siteapp.tests import OrganizationSiteFunctionalTests

class ComponentUITests(OrganizationSiteFunctionalTests):

    component_name = "XYZZY"

    def setUp(self):
        super().setUp()

        self.json_download = \
            self.download_path / PurePath(slugify(self.component_name)).with_suffix(".json")
        print("********* self.json_download", self.json_download)

        # we need a system and a component
        root_element = Element(name="My Root Element",
                               description="Description of my root element")
        root_element.save()
        self.system = System()
        self.system.root_element = root_element
        self.system.save()
        project = self.org.get_organization_project()
        project.system = self.system
        project.save()
        self.system.assign_owner_permissions(self.user)
        statement = Statement(sid='ac-1', 
                              sid_class=Catalogs.NIST_SP_800_53_rev4,
                              body='My statement body',
                              status='Not Implmented')
        statement.save()
        producer_element, created = Element.objects.get_or_create(name=self.component_name)
        statement.producer_element = producer_element
        statement.consumer_element = root_element
        statement.save()

        self.component = producer_element

        # enable experimental OSCAL -and- OpenControl support
        enable_experimental_oscal = \
            SystemSettings.objects.get(setting='enable_experimental_oscal')
        enable_experimental_oscal.active = True
        enable_experimental_oscal.save()

        enable_experimental_opencontrol = \
            SystemSettings.objects.get(setting='enable_experimental_opencontrol')
        enable_experimental_opencontrol.active = True
        enable_experimental_opencontrol.save()

    def tearDown(self):
        # clean up downloaded file
        if self.json_download.is_file():
            self.json_download.unlink()
        super().tearDown()

    def test_component_download_oscal_json(self):
        self._login()
        url = self.url(f"/systems/{self.system.id}/component/{self.component.id}")
        self.browser.get(url)
        self.click_element('a[href="#oscal"]')

        # sigh; selenium doesn't really let us find out the name of the
        # downloaded file, so let's make sure it doesn't exist before we
        # download
        # definite race condition possibility

        if self.json_download.is_file():
            self.json_download.unlink()
        self.click_element("a#oscal_download_json_link")
        var_sleep(2)            # need to wait for download, alas
        # assert download exists!
        self.assertTrue(self.json_download.is_file())
        # assert that it is valid JSON by trying to load it
        with open(self.json_download, 'r') as f:
            json_data = json.load(f)

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

    def test_element_copy(self):
        """Test copying an element"""

        # Create an element
        e = Element.objects.create(name="OAuth", full_name="OAuth Service", element_type="component")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "OAuth")
        e.save()

        # Create smts of type control_implementation_prototype for element
        smt_1 = Statement.objects.create(
            sid = "au-3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is the first test statement.",
            statement_type = "control_implementation_prototype",
            status = "Implemented",
            producer_element = e
        )
        smt_1.save()
        smt_2 = Statement.objects.create(
            sid = "au-4",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is the first test statement.",
            statement_type = "control_implementation_prototype",
            status = "Implemented",
            producer_element = e
        )
        smt_2.save()

        # Make a copy of the element
        e_copy = e.copy()
        e_copy.save()

        # Test element copied
        self.assertTrue(e_copy.id is not None)
        self.assertFalse(e_copy.id == e.id)
        self.assertTrue(e_copy.name == "OAuth copy")

        # Test statements copied
        smts = e_copy.statements("control_implementation_prototype")
        self.assertEqual(len(smts), 2)

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
        poam = Poam.objects.create(statement = smt, poam_group = "New POA&M Group")
        self.assertTrue(poam.poam_group == "New POA&M Group")
        # self.assertTrue(poam.name == "New Element")
        # self.assertTrue(poam.full_name == "New Element Full Name")
        # self.assertTrue(poam.element_type == "system")
        poam.save()
        # poam.delete()
        # self.assertTrue(poam.uuid is None)

class ControlComponentTests(OrganizationSiteFunctionalTests):

    def create_test_statement(self, sid, sid_class, body, statement_type, status):
        """
        Creates and saves a new statement
        """
        # Create a smt
        smt = Statement.objects.create(
            sid = sid,
            sid_class = sid_class,
            body = body,
            statement_type = statement_type,
            status = status
        )
        smt.save()
        return smt

    def click_components_tab(self):
        self.browser.find_element_by_partial_link_text("Component Statements  ").click()

    def dropdown_option(self, dropdownid):
        """
        Allows for viewing of attributes of a given dropdown/select
        """

        dropdown = Select(self.browser.find_element_by_id(dropdownid))
        return dropdown

    def create_fill_statement_form(self, name, statement, part, status, statusvalue, remarks):
        """
        In the component statements tab create and then fill a new component statement with the given information.
        """

        self.click_components_tab()

        # Click to add new component statement
        self.click_element("#new_component_statement")

        # Open the new component form open
        self.browser.find_element_by_link_text("New Component Statement").click()

        # Fill out form
        self.browser.find_element_by_id("producer_element_name").send_keys(name)
        self.browser.find_elements_by_name("body")[-1].send_keys(statement)
        self.browser.find_elements_by_name("pid")[-1].send_keys(part)
        select = self.dropdown_option(status)
        select.select_by_value(statusvalue)
        self.browser.find_elements_by_name("remarks")[-1].send_keys(remarks)
        # Save form
        self.browser.find_elements_by_name("save")[-1].click()
        self.browser.refresh()

    def test_smt_autocomplete(self):
        """
        Testing if the textbox can autocomplete and filter for existing components
        """

        # login as the first user and create a new project
        self._login()
        self._new_project()
        var_sleep(1)


        # Select moderate
        self.navigateToPage("/systems/1/controls/baseline/NIST_SP-800-53_rev4/moderate/_assign")
        # Head to the control ac-3
        self.navigateToPage("/systems/1/controls/catalogs/NIST_SP-800-53_rev4/control/ac-3")

        statement_title_list = self.browser.find_elements_by_css_selector("span#producer_element-panel_num-title")
        assert len(statement_title_list) == 0

        # Creating a few components
        self.create_fill_statement_form("Component 1", "Component body", 'a', 'status_',"Planned", "Component remarks")
        self.create_fill_statement_form("Component 2", "Component body", 'b', 'status_',"Planned", "Component remarks")
        self.create_fill_statement_form("Component 3", "Component body", 'c', 'status_',"Planned", "Component remarks")
        self.create_fill_statement_form("Test name 1", "Component body", 'a', 'status_',"Planned", "Component remarks")
        self.create_fill_statement_form("Test name 2", "Component body", 'b', 'status_',"Planned", "Component remarks")
        self.create_fill_statement_form("Test name 3", "Component body", 'c', 'status_',"Planned", "Component remarks")

        self.click_components_tab()

        # Confirm the dropdown sees all components
        comps_dropdown = self.dropdown_option("selected_producer_element_form_id")
        assert len(comps_dropdown.options) == 6
        # Click on search bar
        search_comps_txtbar = self.browser.find_elements_by_id("producer_element_search")

        # Type a few text combinations and make sure filtering is working
        # Need to click the new dropdown after sending keys

        ## Search for Component
        search_comps_txtbar[-1].click()
        search_comps_txtbar[-1].clear()
        search_comps_txtbar[-1].send_keys("Component")
        self.browser.find_elements_by_id("selected_producer_element_form_id")[-1].click()
        var_sleep(3)
        assert len(comps_dropdown.options) == 3

        ## Search for 2
        search_comps_txtbar[-1].click()
        search_comps_txtbar[-1].clear()
        search_comps_txtbar[-1].send_keys("2")
        self.browser.find_elements_by_id("selected_producer_element_form_id")[-1].click()
        var_sleep(3)
        assert len(comps_dropdown.options) == 2

        # Add a new component based on one of the options available in the filtered dropdown

        ## Test name 2 has a value of 6 and Component 2 has a value of 3
        self.select_option("select#selected_producer_element_form_id", "6")
        assert self.find_selected_option("select#selected_producer_element_form_id").get_attribute("value") == "6"

        self.select_option("select#selected_producer_element_form_id", "3")
        assert self.find_selected_option("select#selected_producer_element_form_id").get_attribute("value") == "3"

        # Open a modal will with component statements related to the select component prototype
        add_related_statements_btn = self.browser.find_elements_by_id("add_related_statements")
        add_related_statements_btn[-1].click()

        # Ensure we can't submit no component statements and that the alert pops up.
        self.browser.find_element_by_xpath("//*[@id='relatedcompModal']/div/div[1]/div[4]/button").click()

        # Open the first panel
        component_element_btn = self.browser.find_element_by_id("related-panel-1")
        component_element_btn.click()

        select_comp_statement_check = self.browser.find_element_by_name("relatedcomps")
        select_comp_statement_check.click()

        # Add component statement
        submit_comp_statement = self.browser.find_element_by_xpath("//*[@id='relatedcompModal']/div/div[1]/div[4]/button")
        submit_comp_statement.click()

        self.click_components_tab()

        statement_title_list = self.browser.find_elements_by_css_selector("span#producer_element-panel_num-title")
        assert len(statement_title_list) == 7

