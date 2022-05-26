
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
import unittest
from pathlib import PurePath
import tempfile
from django.test import TestCase
from django.utils.text import slugify
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from controls.models import System
from controls.models import STATEMENT_SYNCHED, STATEMENT_NOT_SYNCHED, STATEMENT_ORPHANED
from controls.views import OSCALComponentSerializer, OSCAL_ssp_export
from siteapp.models import User, Organization, OrganizationalSetting
from siteapp.tests import SeleniumTest, var_sleep, OrganizationSiteFunctionalTests, wait_for_sleep_after
from system_settings.models import SystemSettings
from controls.models import *
from controls.enums.statements import StatementTypeEnum
from controls.oscal import Catalogs, Catalog, de_oscalize_control_id
from siteapp.models import User, Project, Portfolio
from system_settings.models import SystemSettings

from urllib.parse import urlparse

from guardian.shortcuts import assign_perm

#####################################################################


# Control Tests

class Oscal80053Tests(SeleniumTest):
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

class StatementTests(TestCase):

    def test_statement_id_from_control(self):
        cases = (
            ('ac-1', 'a', 'ac-1_smt.a'),
            ('ac-1', '', 'ac-1_smt'),
            ('ac-1.1', 'a', 'ac-1.1_smt.a'),
            ('1.1.1', '', '1.1.1_smt')
        )
        test_func = Statement._statement_id_from_control

        for control_id, part, expected in cases:
            self.assertEqual(test_func(control_id, part), expected)

#####################################################################

class ControlUITests(SeleniumTest):
    def test_homepage(self):
        self.browser.get(self.url("/controls/"))

    def test_control_lookup(self):
        self.browser.get(self.url("/controls/catalogs/NIST_SP-800-53_rev4/control/au-2"))
        wait_for_sleep_after(lambda: self.assertInNodeText("AU-2", "#control-heading"))
        wait_for_sleep_after(lambda: self.assertInNodeText("Audit Events", "#control-heading"))

    def test_control_enhancement_lookup(self):
        self.browser.get(self.url("/controls/catalogs/NIST_SP-800-53_rev4/control/AC-2 (4)"))
        self.assertInNodeText("AC-2(4)", "#control-heading")
        self.assertInNodeText("Automated Audit Actions", "#control-heading")

    def test_catalog_list(self):
        """
        Check the catalog listing method has the 3 default catalogs
        """

        # os.makedirs(EXTERNAL_CATALOG_PATH, exist_ok=True)
        catalog_list = Catalogs().list_catalogs()
        self.assertEqual(len(catalog_list), 4)

#####################################################################

class ComponentUITests(OrganizationSiteFunctionalTests):

    component_name = "XYZZY"

    def setUp(self):
        super().setUp()

        self.json_download = \
            self.download_path / PurePath(slugify(self.component_name)).with_suffix(".json")
        # print("********* self.json_download", self.json_download)

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

        # enable experimental OpenControl support
        enable_experimental_opencontrol, _  = SystemSettings.objects.get_or_create(setting='enable_experimental_opencontrol')
        enable_experimental_opencontrol.active = True
        enable_experimental_opencontrol.save()

    def tearDown(self):
        # clean up downloaded file if linux elif dos
        if self.json_download.is_file():
            self.json_download.unlink()
        elif os.path.isfile(self.json_download.name):
            os.remove(self.json_download.name)
        super().tearDown()

    @unittest.skip
    def test_component_download_oscal_json(self):
        self._login()
        url = self.url(f"/controls/components/{self.component.id}")
        self.browser.get(url)
        self.click_element('a[href="#oscal"]')

        # sigh; selenium doesn't really let us find out the name of the
        # downloaded file, so let's make sure it doesn't exist before we
        # download
        # definite race condition possibility

        if self.json_download.is_file():
            self.json_download.unlink()
        elif os.path.isfile(self.json_download.name):
            os.remove(self.json_download.name)
        wait_for_sleep_after(lambda: self.click_element("a#oscal_download_json_link"))
        var_sleep(2)
        # assert download exists!
        try:
            # The following test FAILS on MacOS when tests run in HEADLESS mode.
            # Test passes when tests run in visible mode.
            # See: https://github.com/SeleniumHQ/selenium/issues/5292#issuecomment-544264234
            # To use visible mode, add to environment.json file ` "test_visible": true `
            # See: https://govready-q.readthedocs.io/en/latest/testing-for-govready-q/automated-testing.html#for-developers
            self.assertTrue(self.json_download.is_file())
            wait_for_sleep_after(lambda: self.assertTrue(self.json_download.is_file()))
            filetoopen = self.json_download
        except:
            wait_for_sleep_after(lambda: self.assertTrue(os.path.isfile(self.json_download.name)))
            # assert that it is valid JSON by trying to load it
            filetoopen = self.json_download.name
        with open(filetoopen, 'r') as f:
            json_data = json.load(f)
            self.assertIsNotNone(json_data)

        if self.json_download.is_file():
            self.json_download.unlink()
        elif os.path.isfile(self.json_download.name):
            os.remove(self.json_download.name)

    def test_component_import_invalid_oscal(self):
        self._login()
        url = self.url(f"/controls/components")# component library
        self.browser.get(url)
        self.click_element('a#component-import-oscal')
        app_root = os.path.dirname(os.path.realpath(__file__))
        oscal_json_path = os.path.join(app_root, "data/test_data", "test_invalid_oscal.json")
        file_input = self.find_selected_option('input#json_content')
        self.filepath_conversion(file_input, oscal_json_path, "sendkeys")

        element_count_before_import = Element.objects.filter(element_type="system_element").count()
        statement_count_before_import = Statement.objects.filter(
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name).count()

        # Verify that the contents got copied correctly from the file to the textfield
        try:
            # Load contents from file
            with open(oscal_json_path, 'r') as f:
                loaded_oscal_file_json = json.load(f)

            # Load contents from textarea
            file_contents = self.find_selected_option('textarea#id_json_content').get_attribute("value")
            oscal_json_contents = json.loads(file_contents)

            self.assertEqual(loaded_oscal_file_json, oscal_json_contents)

        except ValueError:
            pass

        self.click_element('input#import_component_submit')

        element_count_after_import = Element.objects.filter(element_type="system_element").count()
        self.assertEqual(element_count_before_import, element_count_after_import)

        statement_count_after_import = Statement.objects.filter(statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name).count()
        self.assertEqual(statement_count_before_import, statement_count_after_import)

    def test_component_import_oscal_json(self):
        self._login()
        url = self.url(f"/controls/components")# component library
        self.browser.get(url)

        element_count_before_import = Element.objects.filter(element_type="system_element").count()
        statement_count_before_import = Statement.objects.filter(statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name).count()

        # Test initial import of Component(s) and Statement(s)
        self.click_element('a#component-import-oscal')
        app_root = os.path.dirname(os.path.realpath(__file__))
        oscal_json_path = os.path.join(app_root, "data/test_data", "test_oscal_component.json")
        file_input = self.find_selected_option('input#json_content')
        oscal_json_path = self.filepath_conversion(file_input, oscal_json_path, "sendkeys")

        self.click_element('input#import_component_submit')
        var_sleep(4)
        element_count_after_import = wait_for_sleep_after(lambda: Element.objects.filter(element_type="system_element").count())

        wait_for_sleep_after(lambda: self.assertEqual(element_count_before_import + 1, element_count_after_import))

        statement_count_after_import = Statement.objects.filter(statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name).count()
        self.assertEqual(statement_count_before_import + 1, statement_count_after_import)
        # Test that duplicate Components are re-imported with a different name and that Statements get reimported

        wait_for_sleep_after(lambda: self.click_element('a#component-import-oscal'))

        file_input = self.find_selected_option('input#json_content')
        # Using converted keys from above
        file_input.send_keys(oscal_json_path)

        self.click_element('input#import_component_submit')

        element_count_after_duplicate_import = wait_for_sleep_after(lambda: Element.objects.filter(element_type="system_element").count())

        self.assertEqual(element_count_after_import + 1, element_count_after_duplicate_import)

        original_import_element_count = Element.objects.filter(name='test component 1').count()
        self.assertEqual(original_import_element_count, 1)

        duplicate_import_element_count = Element.objects.filter(name='test component 1 (1)').count()
        self.assertEqual(duplicate_import_element_count, 1)

        statement_count_after_duplicate_import = Statement.objects.filter(
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name).count()
        self.assertEqual(statement_count_after_import + 1, statement_count_after_duplicate_import)

    def test_import_tracker(self):
        """Tests that imports are tracked correctly."""

        self._login()
        url = self.url(f"/controls/components")# component library
        self.browser.get(url)

        # Test initial import of Component(s) and Statement(s)
        self.click_element('a#import_records_link')

        current_path = urlparse(self.browser.current_url).path
        self.assertEqual('/controls/import_records', current_path)

        import_record_links = self.browser.find_elements_by_class_name('import_record_detail_link')
        self.assertEqual(len(import_record_links), 0)

        # Create an Import Record with a component and statement
        helper = ControlTestHelper()
        helper.create_simple_import_record()

        self.browser.refresh()

        import_record_links = wait_for_sleep_after(lambda: self.browser.find_elements_by_class_name('import_record_detail_link'))
        self.assertEqual(len(import_record_links), 1)

    def test_import_delete(self):
        """Tests that import deletions remove child components and statements."""

        # Create an Import Record with a component and statement
        helper = ControlTestHelper()
        import_record = helper.create_simple_import_record()

        self._login()
        url = self.url(f"/controls/import_records")
        self.browser.get(url)

        self.click_element(f"a.import_record_detail_link")
        self.click_element(f"a#delete-import")

        # Test that cancel doesn't delete the import, and redirects to the component library
        self.click_element(f"a#cancel-import-delete")

        current_path = urlparse(self.browser.current_url).path
        self.assertEqual('/controls/components', current_path)

        import_records_count = ImportRecord.objects.all().count()
        self.assertEqual(import_records_count, 1)
        component_count = Element.objects.filter(import_record=import_record).count()
        self.assertEqual(component_count, 1)
        statement_count = Statement.objects.filter(import_record=import_record).count()
        self.assertEqual(statement_count, 1)

        # Test that confirming the deletion deletes the import, component, and statement
        url = self.url(f"/controls/import_records")
        self.browser.get(url)
        self.click_element(f"a.import_record_detail_link")
        self.click_element(f"a#delete-import")

        self.click_element(f"a#confirm-import-delete")

        current_path = urlparse(self.browser.current_url).path

        self.assertEqual('/controls/components', current_path)

        import_records_count = ImportRecord.objects.all().count()
        self.assertEqual(import_records_count, 0)
        component_count = Element.objects.filter(import_record=import_record).count()
        self.assertEqual(component_count, 0)
        statement_count = Statement.objects.filter(import_record=import_record).count()
        self.assertEqual(statement_count, 0)

    def test_element_rename(self):
        # Ensures that the edit button doesnt appear for non-superusers
        # Logs into a non-superuser account and goes to a components page
        self._login()
        url = self.url(f"controls/components/{self.component.id}")
        self.browser.get(url)
        # Asserts that the edit button element is not found on the page
        self.assertTrue(len(self.browser.find_elements_by_css_selector('#edit-button'))<1)

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
            sid = "au-3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is a test statement.",
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
            status = "Implemented"
        )
        smt.save()
        # orphaned w/o prototype
        self.assertEqual(smt.prototype_synched, STATEMENT_ORPHANED)

        # Create statement prototype
        smt.create_prototype()
        self.assertEqual(smt.body, smt.prototype.body)
        self.assertNotEqual(smt.id, smt.prototype.id)
        self.assertEqual(smt.prototype_synched, STATEMENT_SYNCHED)

        # Change statement compared to prototype
        smt.prototype.body = smt.prototype.body + "\nModified statememt"
        smt.prototype.save()
        self.assertEqual(smt.prototype_synched, STATEMENT_NOT_SYNCHED)
        self.assertEqual(smt.diff_prototype_main, [(0, 'This is a test statement.'), (-1, '\nModified statememt')])

class ElementUnitTests(TestCase):

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
        e = Element.objects.create(name="OAuth", full_name="OAuth Service", element_type="system_element")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "OAuth")
        e.save()

        # Create smts of type control_implementation_prototype for element
        smt_1 = Statement.objects.create(
            sid = "au-3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is the first test statement.",
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name,
            status = "Implemented",
            producer_element = e
        )
        smt_1.save()
        smt_2 = Statement.objects.create(
            sid = "au-4",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is the first test statement.",
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name,
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
        smts = e_copy.statements(StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name)
        self.assertEqual(len(smts), 2)

    def test_element_rename(self):
        """Test renaming an element"""

        # Create an element
        e = Element.objects.create(name="Element A", full_name="Element A Full Name",description="Element A Description",element_type="system_element")
        self.assertIsNotNone(e.id)
        self.assertEqual(e.name, "Element A")
        self.assertEqual(e.description, "Element A Description")
        e.name = "Renamed Element A"
        e.description = "Renamed Element A Description"
        e.save()
        self.assertEqual(e.name, "Renamed Element A")
        self.assertEqual(e.description, "Renamed Element A Description")

    def test_component_type_state(self):
        e = Element.objects.create(name="New component",  element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.component_type == "software")
        self.assertTrue(e.component_state == "operational")
        e2 = Element.objects.create(name="New component2",  element_type="system", component_type="hardware", component_state="disposition")
        self.assertTrue(e2.id is not None)
        self.assertTrue(e2.component_type == "hardware")
        self.assertTrue(e2.component_state == "disposition")

class ElementUITests(OrganizationSiteFunctionalTests):

    def test_element_create_form(self):
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/controls/components"))
        self.click_element("#component-new")
        wait_for_sleep_after(lambda: self.assertInNodeText("New Component", "h2"))
        element_name = "Tanium"
        self.clear_and_fill_field("#id_name", element_name)
        self.clear_and_fill_field("#id_full_name", "Tanium Software")
        self.clear_and_fill_field("#id_description", "Tanium")
        # Submit form
        self.click_element("#create-element-button")
        # Check element/component page
        wait_for_sleep_after(lambda: self.assertInNodeText(element_name, "#element-name"))
        var_sleep(1)
        lockIsPresent =  wait_for_sleep_after(lambda: self.browser.find_element_by_id('lock-glyph'))
        self.assertTrue(lockIsPresent)
        var_sleep(1)

    def test_edit_element_private_to_public(self):
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/controls/components"))
        self.click_element("#component-new")
        wait_for_sleep_after(lambda: self.assertInNodeText("New Component", "h2"))
        element_name = "Tanium"
        self.clear_and_fill_field("#id_name", element_name)
        self.clear_and_fill_field("#id_full_name", "Tanium Software")
        self.clear_and_fill_field("#id_description", "Tanium")
        var_sleep(1)
        # Submit form
        self.click_element("#create-element-button")
        # Check element/component page
        wait_for_sleep_after(lambda: self.assertInNodeText(element_name, "#element-name"))
        var_sleep(1)

        # Check if lock glyphicon is present on the document to signify the Element is private
        lockIsPresent =  wait_for_sleep_after(lambda: self.browser.find_element_by_id('lock-glyph'))
        self.assertTrue(lockIsPresent)

        # Edit component    
        self.click_element("#edit-button")
        # Check if at Edit Component modal
        wait_for_sleep_after(lambda: self.assertInNodeText("Edit Component", "#invitation_modal_title"))
        var_sleep(1)
        
        # Click on checkbox and save
        self.click_element("#private-input")
        var_sleep(1)

        # Click Submit button
        self.click_element("#submit-btn")

        # Check if lock glyph is displayed 
        notThere = False
        # Expecting an exception to be thrown due to the element not being on the page
        try:
            wait_for_sleep_after(lambda: self.browser.find_element_by_id('lock-glyph'))
        except NoSuchElementException:
            print('Lock Glyph does not exist on page')
            pass
        else:
            notThere = True
            pass
        self.assertTrue(notThere)
        var_sleep(3)

        # Changing state of Element back to private
        self.click_element("#edit-button")
        # Check if at Edit Component modal
        wait_for_sleep_after(lambda: self.assertInNodeText("Edit Component", "#invitation_modal_title"))
        var_sleep(1)

        # Click on checkbox and save
        self.click_element("#private-input")
        var_sleep(1)

        # Click submit
        self.click_element("#submit-btn")
        var_sleep(3)

        # Check if lock glyph is displayed 
        glyphPresent = wait_for_sleep_after(lambda: self.browser.find_element_by_id('lock-glyph'))
        
        self.assertTrue(glyphPresent)
        var_sleep(1)

    def test_if_viewer_can_edit_element(self):
        self.browser.get(self.url("/"))
        self._login()
        self.browser.get(self.url("/controls/components"))
        self.click_element("#component-new")
        wait_for_sleep_after(lambda: self.assertInNodeText("New Component", "h2"))
        element_name = "Tanium"
        self.clear_and_fill_field("#id_name", element_name)
        self.clear_and_fill_field("#id_full_name", "Tanium Software")
        self.clear_and_fill_field("#id_description", "Tanium")
        # Submit form
        self.click_element("#create-element-button")
        # Check element/component page
        wait_for_sleep_after(lambda: self.assertInNodeText(element_name, "#element-name"))
        var_sleep(1)
        lockIsPresent =  wait_for_sleep_after(lambda: self.browser.find_element_by_id('lock-glyph'))
        self.assertTrue(lockIsPresent)
        var_sleep(3)

        # Assign view_element role to another user
        print('ASSIGNING VIEW PERMISSION TO USER2\n')
        currentElement = Element.objects.get(name=element_name)
        # currentElement.assign_owner_permissions(self.user)
        assign_perm('view_element', self.user2, currentElement)
        print('ASSIGNED USER2\n')

        # Sign out -> Login with another user -> Check if we can edit
        # Log out
        self.browser.get(self.url("/accounts/logout/"))
        var_sleep(1)

        # Sign in as User2
        self._login(self.user2.username, self.user2.clear_password)
        var_sleep(2)

        self.browser.get(self.url("/controls/components"))
        var_sleep(1)

        # Grab Tanium link element
        wait_for_sleep_after(lambda: self.browser.find_element_by_link_text("Tanium").click())
        var_sleep(1)

        # Check element/component page
        wait_for_sleep_after(lambda: self.assertInNodeText(element_name, "#element-name"))
        var_sleep(1)

        print('Checking if edit button is visible')
        # Edit button should not be visible
        notThere = False
        try:
            wait_for_sleep_after(lambda: self.browser.find_element_by_id('edit-button'))
        except NoSuchElementException:
            print('Edit Button does not exist on page')
            notThere = True
            pass
        self.assertTrue(notThere)
        var_sleep(3)

class ElementControlUnitTests(SeleniumTest):

    def test_assign_baseline(self):

        # Create root_element - no relayed controls should exist
        element = Element(name="sys_root_element")
        element.save()
        self.assertEqual(0,len(element.controls.all()))
        # Create system
        system = System(root_element=element)
        system.save()

        # Create a user because method expect user with correct permission
        user = User(email='jane@example.com', username="Jane")
        user.save()
        # Assign owner permissions
        element.assign_edit_permissions(user)

        # Assign low baseline and some controls should exist
        result = element.assign_baseline_controls(user, 'NIST_SP-800-53_rev4', 'low')
        self.assertLess(110,len(element.controls.all()))
        self.assertGreater(135,len(element.controls.all()))

        # Assign moderate baseline and more controls should exist
        element.assign_baseline_controls(user, 'NIST_SP-800-53_rev4', 'moderate')
        self.assertLess(210,len(element.controls.all()))
        self.assertGreater(280,len(element.controls.all()))

        # Assign low baseline and controls should be removed
        element.assign_baseline_controls(user, 'NIST_SP-800-53_rev4', 'low')
        self.assertLess(110,len(element.controls.all()))
        self.assertGreater(135,len(element.controls.all()))

    def test_element_role(self):
        """Test adding a role to an element"""

        # Create an element and make sure it has an id
        ele = Element.objects.create(name="Element A", full_name="Element A Full Name",description="Element A Description",element_type="system_element")
        self.assertIsNotNone(ele.id)

        # No elements have a role
        self.assertEqual(ele.roles.values_list('role', flat=True).count(), 0)

        ele_role = ElementRole.objects.create(id=1, role="add", description="testing adding a description")
        # Adding the add role to the element
        ele.roles.add(ele_role)

        # One element has a role
        self.assertEqual(ele.roles.values_list('role', flat=True).count(), 1)

        ele2 = Element.objects.create(name="Element B", full_name="Element B Full Name",description="Element B Description",element_type="system_element")
        # Do we have two elements?
        self.assertEqual(Element.objects.all().count(), 2)

        # Even with two elements there is still only one element with a role
        self.assertEqual(ele.roles.values_list('role', flat=True).count(), 1)

class SystemUnitTests(TestCase):
    def test_system_create(self):
        sre = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        self.assertTrue(sre.id is not None)
        self.assertTrue(sre.name == "New Element")
        self.assertTrue(sre.full_name == "New Element Full Name")
        self.assertTrue(sre.element_type == "system")
        s = System(root_element=sre)
        s.save()
        self.assertEqual(s.root_element.name,sre.name)

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

        # Create an element with control implementation statements and assign to system
        e = Element.objects.create(name="OAuth", full_name="OAuth Service", element_type="system_element", component_state="operational")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "OAuth")
        e.save()
        smt_1 = Statement.objects.create(
            sid = "au-3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is the first test statement.",
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
            status = "Implemented",
            producer_element = e,
            consumer_element = s.root_element
        )
        smt_1.save()
        smt_2 = Statement.objects.create(
            sid = "au-4",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is the first test statement.",
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
            status = "Implemented",
            producer_element = e,
            consumer_element = s.root_element
        )
        smt_2.save()

        # Batch update system statements status by changing system component state
        element = e
        control_status = "planned"
        s.set_component_control_status(element, control_status)
        # Test the system's component's statements status were changed
        smt_1_updated = Statement.objects.get(pk=smt_1.id)
        self.assertTrue(smt_1_updated.status, control_status)
        smt_2_updated = Statement.objects.get(pk=smt_2.id)
        self.assertTrue(smt_2_updated.status, control_status)

class SystemUITests(OrganizationSiteFunctionalTests):

    def test_deployments_page_exists(self):

        # login as the first user and create a new project
        self._login()
        self._new_project()

        # systemid = System.objects.all().first()
        project = Project.objects.all().last()
        system = project.system

        self.navigateToPage(f"/systems/{system.id}/deployments")
        # Skip test temporarily in Aspen deployment page
        # TODO: Restore tests
        # wait_for_sleep_after(lambda: self.assertInNodeText("New Deployment", ".systems-element-button"))

        # # Add default deployments to system
        # deployment = Deployment(name="Training", description="Training environment", system=system)
        # deployment.save()

        # # Does new deployment appear on deployments list?
        # self.navigateToPage(f"/systems/{system.id}/deployments")
        # var_sleep(3) # wait for page to open
        # wait_for_sleep_after(lambda: self.assertInNodeText("New Deployment", ".systems-element-button"))

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

class OrgParamTests(SeleniumTest):
    """Class for OrgParam Unit Tests"""

    def test_org_params(self):
        odp = OrgParams()
        self.assertIn('mod_fedramp', odp.get_names())
        odp53 = odp.get_params("mod_fedramp")
        self.assertTrue('at least every 3 years' == odp53['ac-1_prm_2'])
        self.assertEqual(177, len(odp53))

    def test_catalog_all_controls_with_organizational_parameters(self):
        odp = OrgParams()
        self.assertIn('mod_fedramp', odp.get_names())
        odp53 = odp.get_params("mod_fedramp")
        # parameter_values = { 'ac-1_prm_2': 'every 12 parsecs' }
        parameter_values = odp53
        cg = Catalog.GetInstance(Catalogs.NIST_SP_800_53_rev4,
                                 parameter_values=parameter_values)
        cg_flat = cg.get_flattened_controls_all_as_dict()
        control = cg_flat['ac-1']
        description = control['description']
        self.assertTrue('at least every 3 years' in description, description)

    def test_organizational_parameters_via_project(self):

        # for this test, we need a Project, System, and Organization

        # REMIND: it would be nice to refactor all this setup code so
        # it could be easily reused ...

        from guidedmodules.models import AppSource
        from guidedmodules.management.commands.load_modules import Command as load_modules

        try:
            AppSource.objects.all().delete()
        except Exception as ex:
            print(f"Exception: {ex}")
            print(f"App Sources:{AppSource.objects.all()}")
        AppSource.objects.get_or_create(
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
            spec={ # contains a test project
                "type": "local",
                "path": "fixtures/modules/other",
            },
            trust_assets=True
        )\
            .add_app_to_catalog("simple_project")

        user = User.objects.create(
            username="me",
            email="test+user@q.govready.com",
            is_staff=True
        )
        org = Organization.create(name="Our Organization", slug="testorg",
                                  admin_user=user)

        root_element = Element(name="My Root Element",
                               description="Description of my root element")
        root_element.save()

        system = System()
        system.root_element = root_element
        system.save()

        project = org.get_organization_project()
        project.system = system
        project.save()

        parameter_values = project.get_parameter_values(Catalogs.NIST_SP_800_53_rev4)
        self.assertEquals(parameter_values["ac-1_prm_2"], "at least every 3 years")

        # now, add an organizational setting and try again
        OrganizationalSetting.objects.create(organization=org,
                                             catalog_key=Catalogs.NIST_SP_800_53_rev4,
                                             parameter_key="ac-1_prm_2",
                                             value="at least every 100 years")

        # we should now see the organizational setting override
        parameter_values = project.get_parameter_values(Catalogs.NIST_SP_800_53_rev4)
        self.assertEquals(parameter_values["ac-1_prm_2"], "at least every 100 years")

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
        wait = WebDriverWait(self.browser, 15)

        try:
            # Using full Xpath
            comp_tab = self.browser.find_element_by_xpath("/html/body/div[1]/div/div[3]/ul/li[2]/a")
        except:
            # Non-full Xpath with wait
            comp_tab = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '#component_controls')]")))

        comp_tab.click()

    def dropdown_option(self, dropdownid):
        """
        Allows for viewing of attributes of a given dropdown/select
        """

        dropdown = Select(self.browser.find_element_by_id(dropdownid))
        return dropdown

    def create_fill_statement_form(self, name, statement, part, status, statusvalue, remarks, num):
        """
        In the component statements tab create and then fill a new component statement with the given information.
        """

        self.click_components_tab()

        # Click to add new component statement
        self.click_element("#new_component_statement")

        # Open the new component form open
        try:
            new_comp_btn = self.browser.find_element_by_link_text("New Component Statement")
        except:
            new_comp_btn = self.browser.find_element_by_id(f"producer_element-{num}-title")
        new_comp_btn.click()
        # Fill out form
        wait_for_sleep_after(lambda: self.browser.find_element_by_id("producer_element_name").send_keys(name))

        self.browser.find_elements_by_name("body")[-1].send_keys(statement)
        self.browser.find_elements_by_name("pid")[-1].send_keys(part)
        select = self.dropdown_option(status)
        select.select_by_value(statusvalue)
        self.browser.find_elements_by_name("remarks")[-1].send_keys(remarks)
        # Save form
        self.browser.find_elements_by_name("save")[-1].click()
        self.browser.refresh()

    @unittest.skip
    def test_smt_autocomplete(self):
        """
        Testing if the textbox can autocomplete and filter for existing components
        """

        # login as the first user and create a new project
        self._login()
        self._new_project()

        # TODO: Why is system being overridden/conditional. system_id will be 1 in test class and 4 in full test suite
        systemid = System.objects.all().first()
        self.navigateToPage(f"/systems/{systemid.id}/controls/selected")

        # Select moderate
        self.navigateToPage(f"/systems/{systemid.id}/controls/baseline/NIST_SP-800-53_rev4/moderate/_assign")
        # Head to the control ac-3
        self.navigateToPage(f"/systems/{systemid.id}/controls/catalogs/NIST_SP-800-53_rev4/control/ac-3")


        # How many components are there currently?
        # Confirm the dropdown sees all components
        comps_dropdown = wait_for_sleep_after(lambda: self.dropdown_option("selected_producer_element_form_id"))
        num = len(comps_dropdown.options)

        # Create components
        self.create_fill_statement_form("Component 1", "Component body", 'a', 'status_', "Planned", "Component remarks", num)
        num += 1
        wait_for_sleep_after(lambda: self.create_fill_statement_form("Component 2", "Component body", 'b', 'status_', "Planned", "Component remarks", num))
        num += 1
        wait_for_sleep_after(lambda: self.create_fill_statement_form("Component 3", "Component body", 'c', 'status_', "Planned", "Component remarks", num))
        num += 1
        wait_for_sleep_after(lambda: self.create_fill_statement_form("Test name 1", "Component body", 'a', 'status_', "Planned", "Component remarks", num))
        num += 1
        wait_for_sleep_after(lambda: self.create_fill_statement_form("Test name 2", "Component body", 'b', 'status_', "Planned", "Component remarks", num))
        num += 1
        wait_for_sleep_after(lambda: self.create_fill_statement_form("Test name 3", "Component body", 'c', 'status_', "Planned", "Component remarks", num))

        # Refresh page to refresh items in selection
        self.navigateToPage(f"/systems/{systemid.id}/controls/catalogs/NIST_SP-800-53_rev4/control/ac-3")

        wait_for_sleep_after(lambda: self.click_components_tab())

        # Confirm the dropdown sees all components
        comps_dropdown = wait_for_sleep_after(lambda: self.dropdown_option("selected_producer_element_form_id"))


        self.assertEquals(len(comps_dropdown.options), 7)

        # Click on search bar
        search_comps_txtbar = self.browser.find_elements_by_id("producer_element_search")

        # Type a few text combinations and make sure filtering is working
        # Need to click the new dropdown after sending keys

        ## Search for Component
        search_comps_txtbar[-1].click()
        search_comps_txtbar[-1].clear()
        search_comps_txtbar[-1].send_keys("Component")
        self.browser.find_elements_by_id("selected_producer_element_form_id")[-1].click()# Ajax request
        var_sleep(1)
        assert len(comps_dropdown.options) == 3

        ## Search for 2
        search_comps_txtbar[-1].click()
        search_comps_txtbar[-1].clear()
        search_comps_txtbar[-1].send_keys("2")
        self.browser.find_elements_by_id("selected_producer_element_form_id")[-1].click()# Ajax request
        var_sleep(1)
        # print("####### len(comps_dropdown.options)", len(comps_dropdown.options))
        assert len(comps_dropdown.options) == 2
        # Use elements from database to avoid hard-coding element ids expected
        elements = Element.objects.all()
        testname2_ele = str(elements[5].id)
        component2_ele = str(elements[2].id)
        # Add a new component based on one of the options available in the filtered dropdown
        ## Test name 2 has a value of 6 and Component 2 has a value of 3
        self.select_option("select#selected_producer_element_form_id", testname2_ele)
        assert self.find_selected_option("select#selected_producer_element_form_id").get_property("value") == testname2_ele

        ## Test name 2 has a value of 6 and Component 2 has a value of 3
        self.select_option("select#selected_producer_element_form_id", component2_ele)
        assert self.find_selected_option("select#selected_producer_element_form_id").get_property("value") == component2_ele

        # Open a modal will with component statements related to the select component prototype
        add_related_statements_btn = self.browser.find_elements_by_id("add_related_statements")
        add_related_statements_btn[-1].click()
        # Ensure we can't submit no component statements and that the alert pops up.
        wait_for_sleep_after(lambda: self.browser.find_element_by_xpath("//*[@id='relatedcompModal']/div/div[1]/div[4]/button").click())

        # Open the first panel
        component_element_btn = self.browser.find_element_by_id("related-panel-1")
        component_element_btn.click()
        select_comp_statement_check = wait_for_sleep_after(lambda: self.browser.find_element_by_name("relatedcomps"))
        var_sleep(1)
        wait_for_sleep_after(lambda: select_comp_statement_check.click())
        var_sleep(1)
        # Add component statement
        submit_comp_statement = wait_for_sleep_after(lambda: self.browser.find_element_by_xpath("//*[@id='relatedcompModal']/div/div[1]/div[4]/button"))
        submit_comp_statement.click()

class StatementUITests(OrganizationSiteFunctionalTests):

    def test_control_implementation_legacy_ui(self):

       # Test ui
        # login as the first user and create a new project
        self._login()
        if "Warning Message" in self.browser.title:
            self.click_element("#btn-accept")
        self._new_project()

        # systemid = System.objects.all().first()
        project = Project.objects.all().last()
        system = project.system

        # Create a smt
        smt = Statement.objects.create(
            sid = "ac-3",
            sid_class = "NIST_SP-800-53_rev4",
            body = "This is a test legacy statement.",
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_LEGACY.name,
            consumer_element=system.root_element,
            producer_element=system.root_element,
            # status = "Implemented"
        )
        smt.save()

        self.assertEqual(smt.body, "This is a test legacy statement.")

        self.navigateToPage(f"/controls/{system.id}/controls/catalogs/{smt.sid_class}/control/{smt.sid}")

class ProjectControlTests(OrganizationSiteFunctionalTests):

    def test_project_controls_selected(self):

        # login as the first user and create a new project
        self._login()
        if "Warning Message" in self.browser.title:
            self.click_element("#btn-accept")
        self._new_project()

        project = Project.objects.all().last()
        system = project.system
        # Assign low baseline
        result = system.root_element.assign_baseline_controls(self.user, 'NIST_SP-800-53_rev4', 'low')
        # Add component(s)

        self.navigateToPage(f"/systems/{system.id}/controls/selected")
        # var_sleep(10)

        wait_for_sleep_after(lambda: self.assertInNodeText("Selected controls", "#tab-content"))

    # def test_project_control_page(self):

class ControlTestHelper(object):

    def create_simple_import_record(self):
        # Create an Import Record with a component and statement
        import_record = ImportRecord.objects.create()
        import_record.save()

        component = Element.objects.create(
            name='Test Component',
            description='This is a test component',
            element_type="system_element",
            import_record=import_record,
        )
        component.save()

        statement = Statement.objects.create(
            sid='ac-7',
            sid_class='NIST_SP-800-53_rev4',
            pid='a',
            body='This is a sample statement',
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
            producer_element=component,
            import_record=import_record,
        )
        statement.save()

        return import_record

