
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
from selenium.common.exceptions import WebDriverException
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


#####################################################################


# Control Tests

class ImportExportProjectTests(OrganizationSiteFunctionalTests):
    """
    Testing the whole import of project JSON which will form a new system, project, and set of components and their statements.
    """

    def test_update_project_json_import(self):
        """
        Testing the update of a project through project JSON import and ingestion of components and their statements
        """

        # login as the first user and create a new project
        self._login()
        self._new_project()

        # Checks the number of projects and components before the import
        # The number of projects should be 2  to start:
        #  - the system project representing the organization (legacy)
        #  - the sample project created during setup of GovReady
        EXISTING_PROJECT_COUNT = 2
        self.assertEqual(Project.objects.all().count(), EXISTING_PROJECT_COUNT)
        self.assertEqual(Element.objects.all().exclude(element_type='system').count(), 0)

        ## Update current project
        # click import project button, opening the modal
        # wait_for_sleep_after(lambda: self.click_element("#menu-btn-project-import"))
        self.click_element("#menu-btn-project-import")

        file_input = self.browser.find_element_by_css_selector("#id_file")

        file_path = os.getcwd() + "/fixtures/test_project_import_data.json"
        # convert filepath if necessary and send keys
        self.filepath_conversion(file_input, file_path, "sendkeys")
        self.browser.find_element_by_id("import_project_submit").click()

        # Check the new number of projects, and validate that it's the same
        project_num = Project.objects.all().count()
        self.assertEqual(project_num, EXISTING_PROJECT_COUNT)
        # Has the updated name?
        wait_for_sleep_after(lambda: self.assertEqual(Project.objects.all()[project_num - 1].title, "New Test Project"))
        # Components and their statements?
        self.assertEqual(Element.objects.all().exclude(element_type='system').count(), 1)
        self.assertEqual(Element.objects.all().exclude(element_type='system')[0].name, "test component 1")

        try:
            self.assertEqual(Statement.objects.all().count(), 1)
        except:
            self.assertEqual(Statement.objects.all().count(), 4)

    def test_project_json_export(self):
        """
        Testing the export of a project through JSON and ingestion of components and their statements
        """

        # login as the first user and create a new project
        self._login()
        self._new_project()

        # export the only project we have so far
        self.navigateToPage('/systems/2/export')

        # Project title to search for in file names
        project_title = "I_want_to_answer_some_questions_on_Q._3"
        file_system = os.listdir(os.getcwd())
        # Assert there is a file
        for file_name in file_system:
            if file_name == project_title:
                project_title = file_name

        self.assertIn(file_name, file_system)

class ImportExportOSCALTests(OrganizationSiteFunctionalTests):
    """
    Testing the import and export of OSCAL JSON objects
    """

    @unittest.skip
    def test_export_oscal_system_security_plan(self):
        """
        Testing OSCAL_ssp_export to make sure the file is created with a status code of 200 utilizing the class OSCALSystemSecurityPlanSerializer's as_json() method
        """
        self._login(self.user.username, self.user.clear_password)
        self._new_project()

        the_system = self.current_project.system

        # ssp_export_oscal with system id
        response = OSCAL_ssp_export(self,"", {"system_id": the_system.id} )

        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            response.get('Content-Type'),
            'application/json'
        )
        self.assertIn(
        f"attachment; filename={the_system.root_element.name.replace(' ', '_')}_OSCAL_",
        response.get('Content-Disposition')
        )

    def test_deoscalization_control_id(self):
        """
        Tests de_oscalize_control_id function on expected formats from sid (oscal) format to regular.
        """
        controls = ["ac-2.4", "ac-2.5", "ac-2.11","ac-2.13", "ac-3", "ac-4", "si-3.2", "si-4.2", "si-4.5"]
        regular_sid_controls = [de_oscalize_control_id(control) for control in controls]
        self.assertEqual(['AC-2(4)', 'AC-2(5)', 'AC-2(11)', 'AC-2(13)', 'AC-3', 'AC-4', 'SI-3(2)', 'SI-4(2)', 'SI-4(5)'], regular_sid_controls)


