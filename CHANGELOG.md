GovReady-Q Release Notes
========================

v0.10.1.1-dev (June 29, 2022)
-----------------------------

**Buf fixes**

* Hot patch to fix OSCAL SSP generation by making sure security_sensitivity_level has value.

v0.10.1-dev (June 28, 2022)
---------------------------

**Security fixes**

* Upgrade npm modules to address multiple vulnerabilities.


v0.10.0 (June 24, 2022)
-----------------------

Welcome to GovReady-q v0.10.0 "Aspen".

The Aspen release provides major feature and stability improvements to the GovReady-Q GRC software.

Version 0.10 Aspen contains multiple, customer-driven improvements:

* Over 150 sample components based on DOD STIGs and SRGs.

* Private components, component usage approvals, and component responsible roles.

* An integrations framework for interacting with third-party APIs including other GRC software.

* Improved questionnaire editing screens.

* Major bug fixes.

* More generous MIT open source license.

The Aspen release has been under stealth development with select customers for 10 months
and provides a solid foundation for even more exciting innovations to come.

    *******************************************************************************
    * IMPORTANT! RELEASES BETWEEN v0.9.11.2 and v0.10.0 CONTAIN BREAKING CHANGES! *
    *             PLEASE READ CHANGELOGS FOR ALL VERSIONS!                        *
    *******************************************************************************

**Feature changes**

* Support private components.
* Assign responsible roles to components and appointing parties to roles.
* Integrations framework for better inclusion of information from remote services.
* Component usage approval workflow.
* Single Sign On OIDC support.
* New questionnaire authoring and editing interface.
* Over 150 sample components created from DOD STIGS.
* Add form to create system from string or URLs.

**UI changes**

* Change label 'certified statement' to 'reference statement'.
* Warning Message appears at the top of home page and login page while using an Internet Explorer browser informing the user of Internet Explorer not being supported.
* Indicate private components with lock icon.
* Edit model for component in library supports marking component private.
* Add React component UI widget for setting and editing permissions on component editing.
* Add ability to change privacy of a component is given only to the owner of the component.
* Added tabs for coponent requests.
* Only Component owner can edit user permissions.
* Display the control framework along side of controls in component control listing page.
* Remove icons from project listing.
* Add Component search filter to filter results to components owned by user.
* Add form to create system from string or URLs.
* Change language in interface to 'system, systems' instead of 'project, projects'.
* Navigate users to new system form page as starting point to creating new systems.

**Developer changes**

* Add support for OIDC SSO configuration separate from OKTA SSO configuration.
* Update Django, libraries.
* Remove debug-toolbar.
* Support for private components by adding 'private' boolean field to controls.models.Element.
* Support for hidden components by adding 'hidden' boolean field to controls.models.Element.
* Support for requiring approval components by adding 'require_approval' boolean field to controls.models.Element.
* Create new components as private and assign owner permissions to user who created the component.
* Added extensible Integrations Django appplication to support communication with third-party services via APIs, etc.
* Added initial support for DoJ's CSAM integration.
* Added ElementPermissionSerializer for component (element) permissions.
* Add tests for component creation form user interface.
* Add ElementPermissionSerializer, UpdateElementPermissionSerializer, RemoveUserPermissionFromElementSerializer for component (element) permissions.
* Add ElementWithPermissionsViewSet for component (element) permissions.
* Add more permission functions to element model: assigning a user specific permissions, removing all permissions from a user, and checking if a user is an owner of the element.
* Updated User model to include search by 'username' and exclusion functionality to queryset.
* Add model Roles, Party, and Appointments to siteapp to support identifying roles on Components (Element).
* Assign owners to components imported via OSCAL. If no user is identified during component (element creation) assign first Superuser (administrator) as component owner.
* Support navigating to specific tab on component library component page using URL hash (#) reference.
* Protype integrations System Summary page.
* Refactor and OIDC authentication for proper testing of admin and not admin roles.
* Create a new system via name given by a string in URL.
* Add a large set of sample components (150+) generated from STIGs.
* Detect Apple ARM platform (e.g. 'M1 chip') and use alternate backend Dockerfile with Chromium install commented out.
* Added SystemEvent object in controls to track system events.

**Bug fixes**

* Fix permissions for non-admin members of projects to edit control implementation statements.
* Fix User lookup to properly query search results and exclude specific users
* Resolve components not displaying the tag widget by properly setting existingTags default for new component.
* Footer fixes.
* Assign owners to default components (elements) created during install first_run script.
* Correctly display POA&M forms with left-side menu.
* Refactor and OIDC authentication for proper testing of admin and not admin roles.

**Security fixes**

* Upgrade npm modules to address multiple vulnerabilities.
* Upgrade Python libraries to address multiple vulnerabilities.

v0.9.13 (January 23, 2022)
--------------------------

**UI changes**

* Add sign-in warning message to which users need to agree.
* Reduce number of Group Django messages from question actions into single message for adding actions.
* Simplify new authoring tool. Move prompt from right to left. Only show first line of question prompt.
* Display all project modules in a single group on project.html.
* Display project root_task's module summary on project page.
* Add ability to search projects.

**Bug fixes**

* Properly close CSV export modal after exporting.

**Developer changes**

* Comment out deprecated queries in SiteApp.models.Project.get_projects_with_read_priv.
* Require login to view projects list.

v0.9.11.11 (January 15, 2022)
-----------------------------

**Feature changes**

* Ability to add modules in new authoring tool.
* Allow deleting of questions, modules in new authoring tool by removing protection on foreign key references.
* Superusers can see all projects.

**UI changes**

* Simplify task progress history. Only display questions of current module. Only colorize to glyphicons.
* Enable adding component control statement from System selected component.
* Enable adding component control statement from System selected controls.
* Switch to "I want to..." language on landing page.
* Align module text left and add numbers to project page.
* Add big button back to project home page on module summary page.
* Edit AppVersion title, version, and description in new authoring tool.
* Reinstate Database Administration opening in new browser tab.
* Display pagination control btm of component page.
* Add 'Things to do' text to project.html.
* Display links to previous and next selected control on System selected control editor page.
* Fix sizing of catalog listing panel in app store to keep rows clean.

**Bug fixes**

* Stop scrunching of progress-project-area-wrapper on question page.
* Always make sure output param exists in all modules that get edited.
* Fix adding statements to components in library.
* Correctly escape carriage returns in multi-line component descriptions in edit component modal.

**Developer changes**

* Superusers can see all projects.

v0.9.11.10-dev (December 14, 2021)
----------------------------------

Introuduce new authoring tool. Remove authoring tool modal from task question page.

**Feature changes**

* Enabling batch viewing of questions for easier questionnaire authoring.
* Enable editing of artifacts.
* Enabling cloning entire templates in template library.

**Developer changes**

* Add Django `nlp` app to system to support Natural Language Processing of SSPs and statements.
* Include spaCy libraries as part of build.
* Include initial, simplified candidate entity recognition script.
* Remove full text search of statements from component library search because it was slow and returned to many results.
* Add serializers for Modules and ModuleQuestions.
* Refactor siteapp.views.project and templates/project.html to remove vestigial column vs row layout code and previous authoring tools.
* Remove authoring tool modal from task question page.

**UI changes**

* Use left side vertical React navigation menu for project.
* Improve toast message appearance by limiting width.
* Improve styling of project page rollovers make module actions clearer
* Improve styling of template library. Use bootstrap panels for each item.
* Remove authoring tool modal from task question page.

**Bug fixes**

* Fix permissions to allow non-administrator to clone project templates in project template.
* Fix crash when restoring a previous version of a statement.
* Fix setting control baseline by proper use of `update_or_create` in `System.set_security_impact_level`.

v0.9.11.6 (October 13, 2021)
----------------------------

Remove GPL3 License from repository.

**UI changes**

* Use left side vertical nav menu for project.
* Improve appearance of statement editing forms: better shading, better setting of textarea height, overall appearance.
* Remove adding component or new control from a project's control listing.

v0.9.11.5 (October 9, 2021)
---------------------------

Merge and synchronize api-tag work and supporting REACT structures from GovReady-Q-SPA into latest version GovReady-Q-Private (0.9.11.3)

**Feature changes**

* Enable REACT-based api-tags.

**Developer changes**

* Switch from `ElementRole` to `Tag` as value for dynamic actions in questions.
* Provide `root_element` information for `System` SimpleSystemSerializer to make it easier to identify systems by name.

**Data changes**

* Add `created`, `updated` fields to `controls.System` to better align with base serializer.

v0.9.11.4.2 (October 8, 2021)
-----------------------------

**UI changes**

* Fix component status and type to be set only in library rather than in systems.
* Hide impact levels, POA&M status box from project mini-dashboard until UI can be improved.
* Improve look of modules.

v0.9.11.4.1 (October 7, 2021)
-----------------------------

**Feature changes**

* Insert new questions after current question in authoring tool.

v0.9.11.3 (September 28, 2021)
------------------------------

**Feature changes**

* Add new question types `choice-from-data` and `multiple-choice-from-data` to get display choice with options created from dynamic data.
* Enable downloading of a compliance app directory.

**Developer changes**

* Add new question types `choice-from-data` and `multiple-choice-from-data` to get display choice with options created from dynamic data.
* Improve DRY-ness of module serialization.
* Enable downloading of a compliance app directory.

v0.9.11.2.2 (January 11, 2022)
------------------------------

**Developer changes**

* Update requirements.


v0.9.11.2.1 (October 7, 2021)
-----------------------------

**Developer changes**

* Update requirements.


v0.9.11.2 (September 22, 2021)
------------------------------

**Developer changes**

* Update requirements.

v0.9.11.1 (September 19, 2021)
------------------------------

**Developer changes**

* Add orderby option to listcomponents command to generate list of components and ids.

v0.9.11 (September 18, 2021)
----------------------------

IMPORTANT BREAKING CHANGE

This release replaces questionnaire-style account settings (e.g., user profile) with traditional user information form.

**Installing this release will reset all users display names, titles, and profile pics.**

**Please contact info@govready.com for a free, custom fix to preserve this data if desired!!**

Display names will be reset to the username, title set to blank, and profile pics set to blank.

We apologize for not being able to find a practical, transparent solution to preserve existing display name
and photos during this change. We think the short term pain of resetting of this information at each user's convenience
is better than a complicated attempt to coordinate every install through a fragile, sequence-dependent, multi-version upgrade process.

Until now, user profile information was set by gathering information via our questionnaire feature.
We thought that was cool, but turned out to be overly complex to support. Having a traditional account
settings feature provides for better extensibility and easier use. We've been wanting to make this change for a while.

**Feature changes**

* Replace questionnaire-style account settings (e.g., user profile) with traditional user information form.
* Add a set of default headers (through hidden inputs and a html form) for the SSP CSV export, dubbed Quick CSV.
* Add makecmmcstatements admin command to create library component statements with CMMC content based on existing content.
* Create RemoteStatement model in controls to better track relationship between statements created from other statements.
* Add `change_log` field to maintain more accessible history of changes made to statement.
* Fixed Selenium to run properly in visbile mode while using Docker. Includes changes to `environment.json`
* GovReady-q container name changed from `govready_q_dev` to `govready-q-dev` in all commands.

**UI changes**

* A Quick CSV button on the system security plan page.

**Bug fix**

* Correctly handle exporting library components when component has zero statements to avoid crashing exportcomponentlibrary command.
* Add execute permissions to `/dev_env/docker/remote_interpreter/python_env.sh b/dev_env/docker/remote_interpreter/python_env.sh`
* Fix control group titles not showing up in properly in generated SSPs.
* Replace common Unicode characters in generated SSPs (e.g. smart apostrophe, bullets).

**Developer changes**

Change in `environment.json` to better support visible Selenium tests will require deleting current containers and artifacts for local development. On next launch, run:

```
cd dev_env
rm docker/environment.json
python run.py wipedb
python run.py init
python run.py dev
```

NOTE: GovReady-q container name changed from `govready_q_dev` to `govready-q-dev`.

* Replace questionnaire-style account settings (e.g., user profile) with traditional user information form.
* Add a set of default headers (through hidden inputs and a html form) for the SSP CSV export, dubbed Quick CSV.
* Add makecmmcstatements admin command to create library component statements with CMMC content based on existing content.
* Create RemoteStatement model in controls to better track relationship between statements created from other statements.
* Add `change_log` field to maintain more accessible history of changes made to statement.
* Refactoring profiles to be standard profiles instead of a special case compliance app. See issue #633.
* Add listcomponents command to generate list of components and ids.

**Data changes**

* Add letter 'c' prefix to 800-171 rev 2 control ids to be compliant with NIST OSCAL.
* Add `name`, `title` fields to `siteapp.models.User`.
* Set all user's `name` to `username` as part of data migration.
* Add Speedy SSP with CMMC catalog.

v0.9.10.1 (August 16, 2021)
---------------------------

**Developer changes**

* Add `--stopinvalid` and `--no-stopinvalid` to manage behavior on Trestle validation errors during bulk import of components.

v0.9.10 (August 16, 2021)
-------------------------

**Developer changes**

* Component tags now correctly included on OSCAL component export and included on OSCAL component import.
* Component tags now correctly included on OSCAL SSP generation.

**Bug fix**

* Add the catalog_key to statement's `sid_class` and `source` fields when adding new statement to a component in library.

**Data fix**

* Add migration in controls to load default control catalogs into CatalogData in database. Remove loading of catalogs via first_run command.

v0.9.9 (August 12, 2021)
------------------------

**UI changes**

* Improve speed control selection auto-complete.
* Various improvements to domponent add statement form: better alignment, validate control selected before saving, show/hide "Add component statement" button appropriately.

**Developer changes**

* Move creation of users in first_run to earlier in script.
* Use faster bulk_create importing components.

**Data changes**

* Update sample components to OSCAL 1.0.0.
* Change CatalogData JSONFields to Django JSONField for better searching options.
* Import components and their statements even when catalog not found or statement control ids are not found in referenced catalog.

v0.9.8 (August 09, 2021)
------------------------

**Developer changes**

* Add SystemSettings `auto_start_project` to permit the automatic start of a particular project and automatic start of a question.
* Add questions actions to redirect to project home page or project components.
* Support auto start of project via global System Setting.
* Create new route for displaying a single system component control.
* New controls.models.System property producer_elements_control_impl_smts_dict to get dictionary of control implementation statements associated with a system element.
* New controls.models.System property producer_elements_control_impl_smts_status_dict to get dictionary of status of control implementation statements associated with a system element.

**Data changes**

* Add JSONfield `value` to SystemSettings model to support specific detail values.
* Retrieve Catalog data from database instead of file system with new controls.models.CatalogData model.

v0.9.7 (August 06, 2021)
------------------------

**UI changes**

* Display datagrid question wider and with smaller fonts.
* Display existance of legacy statement in project system's selected controls.

**Developer changes**

* Support datagrid specifying select type cell.
* Added new function OSCAL_ssp_export in order to export a system's security plan in OSCAL, this replaces the usual JSON export. Added a several fields of data for OSCAL SSP.
* If a component to be imported has a catalog key that is not found in the internal or external catalog list then it will be skipped and logged.
* If no statements are created the resulting element/component is deleted.
* Component and System Security Plan exports pass OSCAL 1.0.0 schema validation.
* Added a proxy for parties and responsible parties for component OSCAL export.
* Coverage 6.0b1 starts to use a modern hash algorithm (sha256) when fingerprinting for high-security environments, upgrading to avoid this safety fail.
* Validate Component import and SSP with trestle the package.
* **Bug fixes**
* Fix count on project system's components associated with a control (avoid double counting).

v0.9.6 (July 15, 2021)
----------------------

**UI changes**

* Display legacy control implementation statements within system's statements.
* Added compare components button to compare one component's statements to other selected components.
* Added a Select/Deselect button for component comparison choice.
* Add accordion to assessment page to provide information on getting data from Wazuh.
* Add form to Assessments page to collect Wazuh information.
* Support auto start of project via global System Setting.

**Bug fixes**

* Set component library detail page Systems tab to not be inactive and thus remove the content from the System tab showing up on the Control Implementation Statements tab.

**Developer changes**

* Add custom Django command to batch import legacy control implementation statements from legacy SSPs Excel spreadsheet exports. Currently supports CSAM.
* Added missing unit test for portfolio project endpoint.
* Add `sec_srvc.SecurityService` class to represent a security service from which data could be collected.
* Add SystemSettings `auto_start_project` to permit the automatic start of a particular project and automatic start of a question.
* Add questions actions to redirect to project home page or project components.

**Data changes**

* Set all `StatementTypeEnum.<LABEL>.value` to `StatementTypeEnum.<LABEL>.name` in order for relevant label/term to show up in Django database admin interface.
* Create baselines for CMMC catalog.
* Fisma impact level is now represented as Security Sensitivity level following OSCAL's schema.
* Add JSONfield `value` to SystemSettings model to support specific detail values.

v0.9.5 (June 23, 2021)
----------------------

**Feature changes**

* Add full text search of component statements in component library search.
* Add tab to component library component detail page to display list of systems containing the component.

**UI changes**

* Add "Import AppSource" button for admins in Compliance App store to simplify end-users adding AppSource.
* Link to library version of component from a system's selected control component listing and selected components.
* Improve UI of project security objectives. Improve alignment and convert text fields to select boxes to control data input.

v0.9.4 (June 13, 2021)
----------------------

**Data changes**

* Require components to have descriptions.
* Adding component_state and component_type fields to an `Element` to contain a component's state and type.
* Created a modal to allow an admin user to add security objectives confidentiality, integrity, and availability.
* Add field to identify user's default portfolio.

**UI changes**

* Can now edit a system componet's state and type in the detail page for a selected component.
* Can now create a component with a state and type with the `ElementForm`
* Improve project pages appearance: decrease action button width and left align text; widen from 9 to 10 columns main content.
* Remove "Refresh Documents" button on task finished page because caches are now automatically cleared and document content refreshed.
* Display system component component_state and component_type when component is listed for a system.
* Add simple "back" link to question to take user to previous question.
* Add "Create a template" button to template library so admins can create a new template (e.g., compliance app).
* Add option to compare components in component library.
* Remove portfolio selection modal from Start a Project process. Assign new projects to user's default portfolio.
* Remove specifying user default portfolio during registration process.

**Developer changes**

* Add management command `exportcomponentlibrary` to batch export components from library as OSCAL or CSV.
* Add management command `importcomponents` to batch import OSCAL components to library.
* Add `existing_import_record` to importing and creating components to group multiple imports under the same import record.
* Improve generation of components in OSCAL model by removing certain keys when values are none as per specification.
* Task caches are now automatically cleared and document content refreshed when document downloaded.
* Add test for system control page.
* Refactor creating system control statements from component library prototype statements when adding a component from the library to a system and reduce by an order a magnitude the time it takes to add a component to system.
* Create System method to batch update an element's control implementation statements based on the component's state.
* Always display OSCAL tab in component library for component detail (rather than conditional on 'enable_experimental_opencontrol' parameter).
* Add method controls.element.consuming_systems to produce list of systems consuming (e.g., containing) the element.

**Deployment changes**

* The HTTP Content-Security-Policy header is now set to allow browsers to load third-party videos from YouTube.com, Vimeo.com and images from any source.

**Bug fix**

* Fix OSCAL SSP output template failure where statement didn't exist while exporting to OSCAL.
* Fix bug breaking rendering of system's control detail page by removing an errant login_required decorator on a function.
* File upload validator now accepts files with capitalized extensions, e.g. ".JPG".
* File upload validator now recognizes ".jpeg" in addition to ".jpg" extension on JPEG files.

v0.9.3.5.3 (May 16, 2021)
-------------------------

**Bug fixes**

* Fix session timeout handler showing 500 error when returning to app after timeout by adding in @login_required decorator to various views that expect user identity.
* Fix multiple copies of component being returned on search by adding `.distinct()` to end of Django search query.
* Fix high number of controls statements (trying) to added on action by filtering statements to type control_implemention_prototype.
* Have page reload after adding control statement to a component in the library to avoid non-feedback to user and user having to refresh the page.

**Security changes**

* Upgrade to Django 3.2.3 to correct for Snyk indicated vulnerability in Django 3.1.8 https://snyk.io/vuln/SNYK-PYTHON-DJANGO-1279042

**Developer changers**

* Remove documentation-related m2r and sphinx related packages from requirements.in.

v0.9.3.5.2 (May 2, 2021)
------------------------

**Bug fixes**

* Restore css style for component count accidentally deleted.

v0.9.3.5.1 (May 1, 2021)
------------------------

**Bug fixes**

* Fix "missing key" error for `SESSION_SECURITY...` params in `settings.py` when realed environment parameters not defined.

v0.9.3.5 (April 28, 2021)
-------------------------

**UI changes**

* Rearrange Create | Import | Manage component buttons; put "Manage Import Records" button last.
* Add links for "forgot password" and "change password".
* Add control titles to component control listing pages.
* Display control catalog guidance text in `details` tag next to component control implementation statements.
* Add control titles to component control listing pages.
* Better notify users when project implementation statement differs from certified by displaying notice in third column of control detail pages.
* Improve language notifying users that project implementation statement differs from certified. Only difference notice is clickable now.
* Search component library by tag content and make component tags clickable.

**Bug fixes**

* Immediately assign change project perms to user starting project and fix issue that non-admin users were not executing modifications to a project the user started such as setting baseline controls.
* Properly filter system POA&M stat to only count POA&Ms for system.
* Provide better error reporting on import component schema validation; report actual validation error to standout.
* Fix N+1 slow display of component control statements with many statements.

**Developer changes**

* Update stub_app used by compliance_app command for generating compliance app to include "input" and "output" section; and to have folders for templates, utils, and components.
* Developers can now use `docker` & `docker-compose` to deploy a local environment.  This allows devs to work on any Operating System.  Instructions can be found at `dev_env/README.md` folder.
* Set system fisma_impact_level as part of question action to set baseline. Also add fisma_impact_level set/get methods to System model.
* Display system impact level on project page.
* Introduce django-session-security package to allow for setting session time out and alert.

**Data changes**

* Use statement type `fisma_impact_level` to track impact level of a system.
* Add input_type to AppInputs in order to make selections of input files based on type. This will support importing POA&Ms as part of loading and the starting an app.

v0.9.3.4 (April 20, 2021)
-------------------------

**Developer changes**

* Add ability for external catalogs and baselines to be used in GovReady-q projects through the two functions `extend_external_baselines` and `extend_external_catalogs`. This includes two new paths GovReady-q looks at which are EXTERNAL_BASELINE_PATH and EXTERNAL_CATALOG_PATH `~/govready-q/local/controls/data/<baselines/catalogs>`
* Added a `list_catalogs()` method to `Catalog` in order to easily get the `Catalog` objects in a list.
* Allow moving projects between portfolios only by users with appropriate permissions.
* Introducing profiling with nplusone to assist in preventing N+1 views.

**Bug fixes**

* Fixed some issues in code resulting in excessive SQL calls slowing down the application

**UI changes**

* Link mini-dashboards on project page to sensible related pages.
* Improved messaging for the move_project function when user does not have the correct permissions.

v0.9.3.3 (April 13, 2021)
-------------------------

**Feature changes**

* Added support for Remote Interpreter on IDEs for the local Docker deployment.

**UI changes**

* Add "Help" link to global navbar.
* Remove caret glyphicons from global navbar.
* Make conditional admin "Settings" link in global navbar a dropdown menu to include link to Django database admin.
* Simplify task-finished page layout. Move navigation buttons to top.
* Replace "...and we're done" language with "Module Summary".
* Replace questions progress sidebar's project links with more obvious project buttons.
* Display all summary values of a SAR result for each inventory item.

**Developer changes**

* Add `tools/simple_sar_server/wazuh_etl.py` to support Wazuh SCA results in SAR pipeline.

**Bug fixes**

* User now has the ability to edit uploaded files via the admin panel.
* File names now updated properly for all Asset models in the event of an update.
* Added a short README.md to each `modules/systems` folder (account, organization) to avoid seeing the README error when loading modules.

**Developer changes**

* (fields.W903) NullBooleanField is deprecated. Support for it (except in historical migrations) will be removed in Django 4.0. Using BooleanField instead for `siteapp.Project.is_organization_project` and `guidedmodules.AppVersion.system_app`.
* Added version data for the project and the project's compliance app to the exported project json.

**Install fixes**

* Create portfolios for admins when passing in ADMIN setting for automated admin creation during install first-run.
* Create default org 'main' if none exists earlier in the first-run process.
* Fix adding admin user to Help Squad and Reviewers list.
* Install default AppSources and compliance apps only if no AppSources installed.

v0.9.3.2 (April 1st, 2021)
--------------------------

* Added sitename model, separated content (splash.html) on index page from index.html and footer.html as well for branding purposes. Removed erroneous tags and cleaned up some CSS. Breadcrumb (context-bar) is hidden on index page now.

**UI changes**

* Filter System Asessment Result Deployment dropdown to only display System's deployments.

**UI changes**

* Polish SAR summary page: add action buttons, use details tag, other improvements.
* Polish SAR list page: include deployment name.
* Polish Deployment inventory detail page.

**Developer changes**

* Create `tools/simple_sar_server/sar.py` to generate synthetic System Assessment Results (summary) data for testing the assessment pages.
* Create `tools/simple_sar_server/sar_etl.py` as example middleware to transform a SAR to a format GovReady-Q can interpret.
* Display assessment name in Assessment model admin list.

**Data changes**

* Update SAR test data.

**Bug fixes**

* Change database settings to close connections after each request and set all transactions to atomic by default.
* Make sure new users are granted `view app source` permission when user account created via SSO proxy.

v0.9.3.1 (March 23, 2021)
-------------------------

**Feature changes**

* Re-assign system's baseline to different baseline; dynamically batch add and removes controls to change a system's existing baseline to a different baseline (e.g. from moderate to low)
* Enable questionnaire question to process question system actions to set system baseline (e.g., selected controls).
* Enable questionnaire question to process question system actions to set project title and system name.
* Support "actions" functionality associated with question answers.
* Support assigning "roles" to elements.
* Use new "actions" and "roles" functionality to enable question answers to add/delete components from selected components of a system.

**UI changes**

* Rename "App Library" to "Template Library" in nav bar.
* Add "Project Home" button to action button ribbon.
* Top of action button ribbon button order now: "Project Home", "Controls", "Components".

**Developer changes**

* Add processing for question actions targeted at system to handle `system/assign_baseline/<value>` to assign baseline set of controls to a system.
* Add processing for question actions targeted at system to handle `system/update_system_and_project_name/<value>` to set system name and project title.
* Add "actions" to Compliance App questions (e.g., tasks) that are conditionally performed based on question answer(s).
* Add "roles" to identify, organize, and process system elements (e.g., components)

The add action capability is supported by new `actions` item within each defined question.

Actions take the form:

```
  actions:
    - value: <answer_value>
      action: <object>/<verb>/<filter>
      comment: <comment>
```

Example actions:

```
  actions:
    - value: adfs
      action: element/add_role/ADFS
      comment: Add elements assigned AFDS to selected components
    - value: adfs
      action: element/del_role/Azure Active Directory
      comment: Delete elements assigned Azure Active Directory from selected components
```

The following actions are currently supported:

1. `system/assign_baseline/<value>` - Automatically sets the system baseline controls to the selected impact
2. `system/update_system_and_project_name/<value>` - Automatically sets the system, project names
3. `element/add_role/<role_value>` - Automatically add elements to the selected components of a system
4. `element/del_role/<role_value>` - Automatically delete elements from the selected components of a system

- Actions are (currently) performed as part of the processing question answer in guidedmodules, before going to next question.
- Actions should be idempotent.
- Actions almost never re-direct user out of the questionnaire.
- Actions need to be reversible. When a user changes an answer previous action should be undone or modified accordingly.

We connect actions defined in the portable compliance app to GovReady-Q instance data via "roles" dynamically assigned to target objects.
In the initially supported use case, Elements can be assiged Roles via new `ElementRole` model.
The new `ElementRole` model assigns roles to system elements via a Many-to-Many relationship.
ElementRoles and associating Elements to roles is currently be done in Django admin interface.

Roles provide a level of abstraction between an action defined in compliance app and actual objects dynamically assign that role.

ElementRoles also enables categorizing, organizing, filtering, and creating checks around Elements. An example roles might be "internal-only" to make allow checks to be added to prevent accidental disclore.

ElementsRoles differ from more generic tags because the setting of roles should be limited to privileged users and have specific organizational purpose.

Current limitations:

- No tests.
- ElementRoles and Element assignment to roles must be done in Djang admin interface.
- Adding component is done through questionnaire, but if component deleted question does not yet know or update. Need to be able to clear question.
- No handling yet of marking a question unanswered.
- No logging yet of action result to question history.
- Code needs optimization and DRY-ness.
- Roles need to be created manually in the GovReady-Q instance for a compliance app using actions with roles. In the future, when a compliance app is loaded the roles could be created automically. An privileged would still need to assign local elements to roles.

**UI changes**

* Provide messaging feedback when answering a question triggers an action.

**Data changes**

* Added speedysp to q-files' govready-q-files-startpack to demonstrate how fast an SSP can be made.

**Install changes**

* Rename installed sample project to clearly indicate project is sample data.

v0.9.3.0rc1 (March 16, 2021)
----------------------------

New, better install process written in Python.
Include all required static files `siteapp/static` directory as part of GovReady-Q distribution.

**Feature changes**

* Add and delete controls from a system's selected controls.

**UI changes**

* Update 3-column statement layout's "edit" into a glyphicon pencil pulled all the way right, remove extra lines and other small changes.
* Update 3-column statement layout to include column headings.
* Conditionally display remarks in component library using HTML details tag.
* Display tags associated with components (components must currently be set in Django admin.)

New, better install process written in Python.
Include all required static files pre-collected in `static_root` directory as part of GovReady-Q distribution.

* Style searchbox on component library and component library detail page to use search glyphicon to indicate search and remove glyphicon within search box to clear search results.
* Separate user home page (e.g., "/") page from `/project` page to provide a better first use and login experience.
* Display number of projects and portfolios on the new user home page.
* Add delete trash icon to selected control list for users with permission to change system. Include a pop-up confirmation dialog.
* Add popup conformation dialog box for deleting components from system's selected components.
* Add autocomplete select box for adding controls to systems's selected controls page.

**Developer changes**

* New, better install process written in Python.
* Include all required static files pre-collected in `static_root` directory as part of GovReady-Q distribution.
* Replace shell script install script `install-govready-q.sh` with better Python install script `install.py`.
* Now including all static files pre-collected as part of distribution.
* Added tag models, views, urls, migrations for reusability. First model to get tags is Controls.models.Element.
* Adds Snyk Security Scans to CircleCi scanned items include python requirements files requirements.txt, requirements_util.txt, and requirements_mysql.txt.

**Bug fixes**

* Properly populate previously blank "Start project" modal that appeared on component library, component library detail, and some other pages.

v0.9.2.2 (March 10, 2021)
-------------------------

**Developer changes**

* Ensure that the number of controls selected for a project reflect non-duplicate counts of that control.
* Updates to how SSP generation works. Passing in a yaml file to provide metadata for title page. Updated docx template. Revisions to the 800-171 markdown template to remove colspans and support display of title page, toc, etc in DOCX. Edits to associated yaml file as well.

**UI changes**

* removed display of export options ("plain text", "markdown"), leaving docx and html.

**Bug changes**

* Fix Postgres crash error by setting the ProjectAsset Model content hash length to 128 characters.
* Find the correct number of panels by adding implementation statement number when adding a statement to a component in the library.

v0.9.2.1 (March 05, 2021)
-------------------------

**UI changes**

* Improve style sheets for 3 column layout.

**Developer changes**

* Adjust Python libraries to support Python 3.6 to 3.9 and improve dependency license tracking comments.

**Bug changes**

* Fixed display of tabular data from data grid questions in questionnaire output documents including generated SSPs.

v0.9.2 (March 1, 2021)
----------------------

**Feature changes**

* Remove a component and its statements from a system.
* Implemented improved, 3 column editing page UI
* Search/filter components feature added to component library (and for system control implementation page).
* Support multiple reference-documents for generating Word version of SSP and other artififacts.

**UI changes**

* Added a button to system selected component page to remove a component from the system.
* Moved "Add a component" to a system drop down to top of selected component page.
* Added a search text box for each searching of components in the library and their statements.
* Added pagnation to the component library and their statements.
* Added a reset button for explicit resetting of component search.
* Update component control statement editor layout with 3 column layout to make reading control implementation statements easier.

**Developer changes**

* Move inclusion of `edit-component-modal.html` from `base.html` to `components/element_detail_tabs.html`.
* Fix sort control order in `component_library_component` on the `components/element_detail_tabs.html` using the `natsort` package to sort SID correctly.
* Comment out `controls.models.ElementControl.get_controls_by_element` method because it is not being used. Will delete after a few releases if not needed.
* Created a ElementEditForm Django form in conjunction with some functional changes to avoid name collisions issues with component library.

**Data changes**

* Alter Element description field to be blank and none.
* Migration to lengthen django.contrib.auth.User.first_name field to 150 characters (change happened during an upgrade of Django and/or libraries).

**Bug changes**

* Fixed how control id, title, and catalog key are retrieved for component library components.

v0.9.1.52 (February 16, 2021)
-----------------------------

Add System Assessment Report tracking to associate assessments and evidence with the system.
Add initial dynamic status information to the project page.
Project page displays mini-dashboard of compliance stats.

**Feature changes**

* Add System Assessment Report tracking to associate assessments and evidence with the system.
* Add initial dynamic status information to the project page.
* Use default catalog parameters to set default control catalog and baseline.

**UI changes**

* Improve page load times for listings with pagination and ordering for project listing and selected component listing.
* Display projects in pages of 10 and selected components by 5.
* Project page displays mini-dashboard of compliance stats.
  * Number of controls implemented out of count of controls.
  * Number of POA&Ms.
  * Count of system components.
  * Approximate overall compliance based on controls implemented / count of controls.
* Project mini-dashboard now reports controls "addressed" instead of implemented and "% compliance (unassessed)" which uses the number of controls that have at least one statement. This is more accurate representation than saying definitely which control has been assessed as implemented. Will show that in future dashboard items.

**Developer changes**

* Properly restrict statement history access to users with system, staff, or admin permissions.
* Avoid name collisions when cloning a component.
* Replaced function-based views with class-based listview for SelectedComponentsList, ProjectList.
* Default to not use Django Debug Toolbar. Added new `enable_tool_bar` parameter option for `local/environment.json` to allow users to enable(True) or disable(False) the Django Debug Toolbar.
* Adding DummyCache to prevent real caching while running automated tests.
* Refactored use of random package to use secure secrets module.
* Added minor pylint fixes.
* Added the ability to import and export Poams along with the project import/export.
* GovReady will now read compliance app catalog.parameters.catalog_key and catalog.parameters.baseline values to set the selected controls for a system.
* Load sample/default components into component library during installation to provide users with starting set of components.

v0.9.1.51 (February 03, 2021)
-----------------------------

Add System Assessment Report tracking to associate assessments and evidence with the system.
Add initial dynamic status information to the project page.

**Feature changes**

* Add System Assessment Report tracking to associate assessments and evidence with the system.
* Add initial dynamic status information to the project page.

**UI changes**

* Display components alphabetically in component library text listing and in selected components text listing.
* Include a component description and statement count in component library text listing and in selected components text listing.
* Remove admin's "update certified text" option from editing control implmentation statements.
* New pages for System Assessment Report
* Updates to project page for status information and other project information.

**Developer changes**

* Set statements to delete (CASCADE) when producer_element deleted.
* Set statements to delete (CASCADE) when consumer_element deleted.
* Add methods to Element to `get_statements`
* Refactor project deletion to properly delete related System (e.g., project.system.root_element), Statements, ElementControls, POAMS, Deployments.

**Bug fix**

* Fix erroneous control statement save error message.

v0.9.1.50.4 (February 03, 2021)
-------------------------------

**Bug fix**

* Fix importing project to just update the project started.

v0.9.1.50.3 (Feburary 01, 2021)
-------------------------------

**UI changes**

* Remove "Upgrade Project" button from project page action buttons. Upgrade is now in settings page.
* Improve styling of app store items.
* Tweek general styling of project page question page:
  * Remove light gray background from project page, question page, task finished page.
  * Reduce corner radius in focus area blocks.
  * Widen question area.

**Compliance app changes**

* Lightweight-ato compliance app (installed by default) now displays SSP button below action buttons.
* Display "Unknown" when app vendor is set to "None" instead of "none".

**Developer changes**

* Format clean up of style sheets in project, app-store templates.
* added functools.lru_cache() decorator to speed a couple funcs.

v0.9.1.50.2 (January 26, 2021)
------------------------------

Adds support for OSCAL component and statement input for Compliance Apps.
(Currently only supports OSCAL JSON inputs.)
Adds statements to project upon project creation.
Keeps track of app inputs by relating them to the app version.

Includes the following schema update to the app.yaml file of Compliance Apps.
Inputs are supported in the app.yaml file with the following format:

```
input:
- id: <input_id> (string)
  name: <Input Name> (string)
  type: oscal (Only oscal currently supported)
  path: <dir/filename.json> (relative file path)
  group: (optional string)
```

Add deployments to capture system deployments and the inventory items in each deployment.
One system has multiple deployments (e.g., dev, stage, prod) and each deployment contains an inventory of the actual endpoints/items in a deployment of the system. Systems start with several common default (empty) deployments.
The "design" deployment by convention is a special deployment to represent the system architecture.
Deployments maintain a complete version history.
Deployment inventory-items are represented as JSON data object following a scheme that is similar to OSCAL inventory-item section.
Data for deployment inventory-items is assumed to be generated outside of GovReady. It is critical that the inventory items have UUIDs prior to import. Inventory item UUIDs for the life of the instantiated inventory item.
Inventory items in an deployment can be associated with an inventory item in the "design" deployment by referencing the "design" inventory item's UUID. This enablea a virtual persistence of an inventory-item across different instances of the "same" assest, such as a virtual database server.

**Feature changes**

* Add system deployments with inventory items to track instantiations of the system in real assets.
* Add lightweight-ato to default apps so users can get started easier.
* Add the Django admin documentation generator to provide useful documentation for developers.

**UI changes**

* Add deployment index page for listing deployments associated with a system.
* Add deployment form page for creating/editing deployments.
* Add deployment history page.

**Developer changes**

* Add `.coveragerc` configuration file to ensure we cover and run only tests in locally and in Circleci.
* Add `pyup.yml` configuration file to have pyup.io pull requests go against `develop` branch.
* Add controls.Deployment object, related routes, views, templates, and admin to track system deployments and deployment inventory items.
* Add DeploymentForm for Deployment model.
* New '%dict' operator for JSON/YAML output templates
* Pass OSCAL context to JSON/YAML output templates
* New '%dict' operator for JSON/YAML output templates
* Pass OSCAL context to JSON/YAML output templates
* Created a recursive method `wait_for_sleep_after` that wraps around other functions allowing for drastically shorter wait times necessary compared to peppering var_sleeps.
* Update install scripts.
* Update default and recommended `local/environment.json` file from `first_run` and `install-govready-q.sh`.
* By default, set organization name to "main".
* Add optional `PIPUSER` parameter to `install-govready-q.sh` to avoid error of running pip install with `--user` flag in virtual environments.
* Comment out starting GovReady-Q server automatically because too many edge cases exist to execute that well.
* Update install scripts.
* Update default and recommended `local/environment.json` file from `first_run` and `install-govready-q.sh`.
* By default, set organization name to "main".
* Add optional `PIPUSER` parameter to `install-govready-q.sh` to avoid error of running pip install with `--user` flag in virtual environments.
* Comment out starting GovReady-Q server automatically because too many edge cases exist to execute that well.
* Add method `get_answer` guidedmodules.models.Task to easily return answers from a project tasks answers.

**Data changes**

* Add lightweight-ato to default apps so users can get started easier.
* Populate every new system with default deployments design, dev, stage, prod.

v0.9.1.49.1 (January 20, 2021)
------------------------------

Fixes to 0.9.1.49 after merge.

**Bug fixes**

* Remove duplicate appearance of tabs in system selected components
* Remove OSCAL download link from selected control pages because OSCAL for a single control would rarely be downloaded and would require different handling
* Hide a discussion test that is failing to address later (not critical)
* Add notes about testing download OSCAL that on Mac test must be run visible for custom download route to work.

v0.9.1.49 (January 12, 2021)
----------------------------

**IMPORTANT**

ADMIN NOTE: New users registering in your GovReady instance PRIOR TO THIS VERSION may not see any Compliance Apps when starting a project. This bug has been fixed, but ADMINS MUST ADD PERMISSION  "guidedmodules | app source | can view app source" TO EACH USER TO FIX PERMISSIONS FOR EXISTING USERS. SEE DJANGO ADMIN CUSTOMER ACTION "add_viewappsource_permission" TO ADD SELECTIVELY ADD THIS PERMISSION TO USERS.

**Feature changes**

* Add default Organizational Defined Parameter values.
* Track batch imports of components (via OSCAL) into component library for tracking and management purposes; enable deletes of batch imports.
* Support defining multiple allowed hosts via the `local/environment.json` file.
* Allow administrators to change component name and description in Component Library.
* Existing projects can be moved between existing portfolios.
* Edit existing portfolio's title and description.
* Delete existing portfolio.
* Add default Organizational Defined Parameter values.
* Add an autocomplete in component library to look up controls across multiple catalogs for writing a control implementation statement.

**UI changes**

* New dialog in Component Library for importing components in OSCAL JSON format
* New screens for tracking and deleting batch imports of components (via OSCAL) into component library.
* Add "Edit" button in Component Library for Administrators to rename a component.
* Add "Move Project" action button on project page to move project to a different portfolio.
* Add "Edit Portofolio" links on portfolio page for editing portfolio details and deleting portfolio.
* Conditionally show button to delete portfolio if portfolio is empty and user has permission to change portfolio.
* Support a Select2 autocomplete dropdown selection box in the component library to assign a control when authoring a new component control implementation statement for a component in the library.
* You can now click the history button in a given statement's panel in the controls selected implementation statement page or component library.
* Added error messages for any files that fail validation for Comment Attachment uploads

**Data changes**

* Add default Organizational Defined Parameter values.
* Add `validators` argument to the `file` field in the Attachment model.
* Add `history` field in the Statement model. This is the source for the new HistoricalStatement table that captures all Statement history.

**Developer changes**

* New `controls.models.ImportRecord` model for tracking batch imports of components (via OSCAL) into component library.
* New routes and views related for tracking batch imports of components (via OSCAL) into component library.
* Fix OSCAL component import to use "statement" JSON property.
* Support defining multiple allowed hosts via the `local/environment.json` file via new `allowed_hosts` environment parameter.
* Added route `controls/api/controlsselect/` and view `api_controls_select` to get list of controls.
* Modified view `save_smt` to just save prototype statement when statement is being created in the component library.
* Modified template `templates/components/element_detail_tabs.html` to use jQuery select2 for autocomplete and search of catalog of controls to add a control to a component.
* Update hidden sid_class field with catalog human readable name. Add hidden field `form_source` to identufy to save smt view that we are receiving form submission from component library.
* Add 'label' value to `oscal.Catalog.cx.get_flattened_controls_all_as_dict`.
* Introducing model history tracking with django-simple-history.
* Update various Python libraries.
* Add file extension, size and type validation for Comment Attachment uploads.
* Introducing request profiling with pyinstrument.
* Add default `controls.models.OrgParams` class to support basic, default generation of orgizational defined parameters.

**Bug fixes**

* Fix missing "part" field on Component's component statement form and incorrectly displaying the "remarks" field (#1232)
* Fix display of OSCAL into correct tab on system's component's page
* When generating OSCAL component files, emit `statement` elements with ids that correlate with the control catalog.
* New non-admin users did not have the permission to view appsource. Added permission after the new user is created with the SignupForm from allauth.account.forms.

v.0.9.1.48.1 (December 17, 2020)
--------------------------------

**Bug fixes**

* Fix handling of static files. Create new `static-root` directory outside of `siteapp` into which to collect static files.
* Remove bad path reference to select2 javascript libraries in component library page.

v0.9.1.48 (December 15, 2020)
-----------------------------

Add Component Library feature pages and improve UI for managing reuse and "certified" component library.

Properly generate JSON, YAML questionnaire output documents from a JSON (or YAML) output template in the compliance app `output` section. The JSON, YAML output documents are first converted to Python data structures and then populated with information in a variant of Jinja2 substitutions.

Fix tests so they execute successfully in CircleCI.

**Feature changes**

* Support Compliance As Code reuse of statements via "certified" control sets. This capability is enabled by adding having statements sub-typed to `control_implementation_prototype` to support local statements sub-typed to `control_implementation` and `control_implementation_prototype` with the latter representing the "certified" version of a component-control element.  Every `control_implementation` statement type was given a Django foreign key called `prototype` to connect that statement to the "certified" version of the control (e.g., `control_implementation_prototype`). This model supports the features in the UI:

1. Add a component to the system while on components page via autocomplete and create `control_implementation` statements from the `control_implementation_prototype` statements
2. Add a component to the system while on control edit page via autocomplete and create `control_implementation` statements from the `control_implementation_prototype` statements
3. Notify user that the local statement for a component-control (e.g., `control_implementation`) was different than the "certified" statement for the component-control (e.g., `control_implementation_prototype`).
4. Enable viewer to view differences between a component-control (e.g., `control_implementation`) was different than the "certified" statement for the component-control (e.g., `control_implementation_prototype`).
5. To update a "certified" statement, enable an administrator to update (e.g. push) the "certified" statement for the component-control (e.g., `control_implementation_prototype`) text from the a systems' component-control (e.g., `control_implementation`) text.
6. After a "certified" statement was updated, enable user to copy (e.g. pull) the updated "certified" statement for the component-control (e.g., `control_implementation_prototype`) text into other systems' a component-control (e.g., `control_implementation`) text.

* Support generation of JSON, YAML questionnaire output documents with Jinja2 style substitutions, loops, and conditionals. Re-do the 'json' template format to recognize a new %for control structure objects that execute loops.
* Support generation of Word DOCX questionnaire output documents with page numbers, headers, footers, TOC (using pandoc custom reference doc feature).
* Support creating a new component in the library.

**UI changes**

* Add Component Library page listing all available components.
* Add global navbar link to Component Library.
* Remove Common Control tab from control editor.
* Remove redundent listing of control statements from component description tab.
* Display filler text when component does not have a description.
* Move component implementation statement tab to left of combined statement tab in control editor.
* Updating certified text also updates the HTML block showing the certified text with updated certified text on edit pages.
* Add components (system elements) via an autocomplete to a system on system's selected components page.
* Add label/alert above implementation statement edit box when notifying user if local system statement is synchronized with certified control implementation statement.
* Make statement synchronization status lable/alert clickable to reveal certified statement and diff between local and certified.
* Add buttons for copying certified statement into local statement and for admin to update certified statement from local statement.
* Add autocompletes to make it easy to add a new component to a system and the component's respective certified controls.
* Use Select2 box to add component to system's selected component.
* Add route `add_system_component` and related view to add a component to a system's selected component.
* Replace the url pattern routing in v0.9.1.46.4 for directing accounts login to home page with custom templates to override default aullauth templates.
* Use Django messaging when adding a component to system's selected component to provide user with better feedback.

**Data changes**

* Add `copy` method to `Element` data model to create a new element (e.g. component) as a copy of existing component.
* Add `statements` method to `Element` data model to produce a list of statements of a particular `statement_type`.
* Add default Organizational Defined Parameter values in `controls/data/org_defined_parameters`.

**Bug fixes**

* Fix multiple loadings of updated `smt.body` into bootstrap's panel heading section by improved naming of div classes in panel and better targeted update.
* Fix enable_experimental_oscal control. Model method was set incorrectly requiring both enable_experimental_oscal and enable_experimental_opencontrol had to be enabled for either to show up.
* Fix testing issues. Fix tests so they execute successfully in CircleCI.

**Developer changes**

* Default Selenium tests to headless mode. Add new `test_visible` parameter option for `local/environment.json` to force Selenium tests to run in visible or headless mode.
  Add `custom-reference.docx` MS Word DOCX document to `/assets` directory to be used by pandoc when generating MS Word output documents in order to provide page numbers, headers, footers, TOC.
* Significantly refactored indentations in control edtor pages to make code folding and div analysis easier.
* Add an ElementForm to create new components (AKA Elements).
* Modified controls.Statement model to link `control_implementation` statements to
  `control_implementation_prototype` statements. See commit 5083af.
* Add methods for diff'ing (e.g., comparing) a `control_implementation` statement against its prototype statement using Google diff-match-patch.
* Avoid duplicative adding of a component to a system causing duplicate statements.
* Avoiding adding a component with no control implementation statements to a system.
* Add all available control implementation statements of a component to a system, even for controls that are not selected controls.
* Avoid adding duplicate control implementation instance statements to a system by checking in the statement model that we are not creating an instance statement when such and statement from prototype already exists.
* Use Django messaging when adding a component to system's selected component to provide user with better feedback.
* Delete already commented-out contol id look up from system's selected components page.
* The work for a component library and certified controls was performed across three branches that were eventually synchronized (approximately commit 18934669) and merged into the master branch:
  * `autocomplete_statements_#1066`
  * `ge/reuse-0903`
  * `automated-tests-statements`

Under development output document formats `oscal_json`, `oscal_yaml`,
and `oscal_xml` are now replaced with `json`, `yaml`, and `xml` respectively.

Format `xml` still under development and not recommended for regular use.

Formats for `json` and `yaml` now support new Jinja2-like tags to enable
parameter substituion and loops inside those formats while Django handles
them as Python objects:

```
%for
%loop

%if
%then

{{ param }}
```

Example:

```
{ "title" : "{{project.system_info.system_name}}",
"published" : "2020-07-01T00:00:00.00-04:00",
"last-modified" : "2020-07-01T00:00:00.00-04:00",
"version" : "0.0",
"oscal-version" : "1.0-Milestone3",
"new-control-stuff": {
  "%for": "control in system.root_element.selected_controls_oscal_ctl_ids",
  "%loop": {
    "%if": "control.lower() in control_catalog",
    "%then":  {
      "uuid": "{{ system.control_implementation_as_dict[control]['elementcontrol_uuid'] }}",
      "control-id": "{{ control.lower() }}",
      "by-component": {
        "%for": "smt in system.control_implementation_as_dict[control]['control_impl_smts']",
        "%loop": {
          "key": "{{ smt.producer_element.uuid }}",
          "value": { "uuid" : "{{ smt.uuid }}",
            "component-name": "{{   smt.producer_element.name|safe }}",
            "description" : "{{ smt.body|safe }}"
          }
        }
      }
    }
  }
}
```

* Update various libraries. See changes in `requirements.txt`.
* Removed instance of using sys.stderr and replaced with logger for proper logging.
* Fix tests so they execute successfully in CircleCI.
* Add default `controls.models.OrgParams` class to support basic, default generation of orgizational defined parameters.

**Other**

* Updated link to `jquery-ui.min.js` library in `fetch-vendor-resources`.
* Update version checking for v999 develop branch designation.

v.0.9.1.47.1 (December 02, 2020)
--------------------------------

**Developer changes**

* Minor further tweaks to CSS refactoring.

v.0.9.1.47 (December 01, 2020)
------------------------------

**Developer changes**

* Significant refactoring of CSS to replace inline styles from as many pages as possible with classes defined in `css/govready-q.css` stylesheet.

**Bug fix**

* Fix system_settings methods enable_experimental_oscal and enable_experimental_opencontrol to work properly.

v0.9.1.46.4 (November 25, 2020)
-------------------------------

**UI changes**

* Adding a url pattern for accounts login to ensure proper styling. Also added conditionals the views landing that constructs the signup and login forms.

v0.9.1.46.3 (November 20, 2020)
-------------------------------

**UI changes**

* Add OSCAL downlink link to system component page.

v0.9.1.46.2 (November 19, 2020)
-------------------------------

**UI changes**

* Omitting the group breadcrumb if it is None for a given question

v0.9.1.46.1 (November 19, 2020)
-------------------------------

**Developer changes**

* Replace the word 'password' with 'pwd' in comments to reduce false positives in code scanners.
* Replace the word 'key' with 'entry' where possible to reduce false positives in code scanners.

v0.9.1.46 (November 17, 2020)
-----------------------------

Add organizational parameter value substitution for Control guidance and OSCAL.

**Data changes**

* Add `OrganizationalSettings` data model for tracking organizational defined parameters.

**Test fixes**

* Fix siteapp.test to make sure a proper login is performed before testing `/settings` page.

v0.9.1.45.1 (November 5, 2020)
------------------------------

**Developer changes**

* Update various Python libraries (#1052)
* Update jquery to 3.5.1, quill to 1.3.7, bootstrap to 3.4.1 (#1052)

v0.9.1.45 (October 24, 2020)
----------------------------

**Bug fixes**

* Fix bug in v0.9.1.44 that failed to handle case of non-existent ElementControl

**Developer changes**

* Update various Python libraries

v0.9.1.44 (October 16, 2020)
----------------------------

This release significantly decreases the time taking to rendering System Security Plans including OSCAL versions.
Rendering time has been reduced by 97%.

**UI changes**

* Remove display of output documents on task finished page due to performance; only display link to the document

**Bug fixes**

* Significantly improve performance of generating System Security Plans

**Developer changes**

* Remove inclusion of deprecated CommonControls section in controls.models.System
* Adjust siteapp.tests to not look for generated output document
* Add `@cached_property` to `controls.models.System.control_implementation_as_dict` and `controls.models.Statement.producer_element_name` to significantly improve SSP rendering performance

v0.9.1.43 (September 23, 2020)
------------------------------

**Bug fixes**

* Enable all admins to upgrade apps versions.
* Fix `System.producer_elements` property error by removing unneeded `@property` decorator added in Version 0.9.1.42 to `get_producer_elements`.
* Gracefully handle missing ElementControl in `System.control_implementation_as_dict` method to avoid failure to render SSP output templates
* Improve compliance app (questionnaire) upgrade to see upgrades as compatible even if compliance app version changed or the id of modules changes (which is expected to happen in an upgrade).

**UI changes**

* Changes to portfolio detail page to match style of similar pages.
* Stop displaying content recommendations on project page and portfolio pages after a project is 1 or higher.

v0.9.1.42 (September 22, 2020)
------------------------------

**UI changes**

* Add group field to POA&M page to collect related POA&Ms together. (#1010)
* Improve the UI on the task-finish page to display option to download OSCAL versions of SSP (JSON, XML). (#1018, #1026)

**Data changes**

* Add `poam_group` field to POA&M model and form.
* Have `System.control_implementation_as_dict` populate information for all assigned (e.g. selected) controls even if no statement exists for assigned control.
* Have `System.control_implementation_as_dict` generate a random uuid for combined statement. NOTE: This statement is random on each generation.

**Developer changes**

* Support for generating OSCAL versions of SSPs as templates.

**Bug fixes**

* Do not show link to question on imputed answers. Separate test for unanswered question and imputed question in rendering HTML navigation for question. (#1015)

v0.9.1.41 (September 20, 2020)
------------------------------

Enable upgrade of project root_task to more recent version.

**UI changes**

* Convert project settings modal to a separate route, view, and page template.
* Add section on project settings page to upgrade project root_task to more recent version.
* Improve ordering of settings option on new project settings page.

**Data changes**

* Add new methods to Project model to support managing and upgrading project's root_task app after the app has been loaded into the database.

**Developer changes**

* Add management command `upgrade_project` to upgrade a project to a newer version of an app, after the app has been loaded into the database from the admin.
* Add logger entries for successful and failed attempts to upgrade project's root_task app.

**Test changes**

* Add tests for upgrading project root_task to more recent version.

**Documentation changes**

* Document new logger entries for successful and failed attempts to upgrade project's root_task app.

v0.9.1.38.2 (September 20, 2020)
--------------------------------

**Developer changes**

* Remove no longer maintained code for deploying to Pivotal Web Services.

v0.9.1.38 (August 28, 2020)
---------------------------

**Bug fix**

* Updated a library filename to match upstream change, fixed failing Docker build.

**Miscellaneous change**

* Use a specific known good version of CentOS 7 (7.8.2003) rather than just generic 7.

v0.9.1.37 (August 23, 2020)
---------------------------

**UI changes**

Fixed multiple accessibility issues:

- Improve contrast in `/projects`, `/portfolios`, and various control pages (replaced `#888` with `#666`)
- Fix redundant links in `/projects`.
- Add label to `select-portfolio-modal` portfolio form element (and remove extra inclusion of modal from `projects.html` template).
- Add value to hidden `h4` global_modal_title to help with accessibility.
- Properly generate "Start project" content to `/controls`, `catalog`, and other control pages.
- Added accessible `title` parameter to `control-lookup` search box on control pages.
- Properly hide notifications when user is anonymous.
- Do not display start dropdown in navbar when user is anonymous.

**Bug fixes**

- Fix missing form labels in start project portfolio selection modal effecting accessibility.
- Do notget portfolio object in ProjectForm for AnonymousUser.

v0.9.1.36.1 (August 19, 2020)
-----------------------------

**UI changes**

* Allow customizable support page to render HTML tags.

v0.9.1.36 (August 13, 2020)
---------------------------

**Feature changes**

* Create view only access for projects, system to support Auditor/Assessor role

v0.9.1.35 (August 08, 2020)
---------------------------

**UI changes**

* Add customizable support page with content defined in the database via Django Admin.
* Improve rendering of controls implementation statements to show control parts.
* Improve rendering of control implemenentation status for better readability. Display as list of options.

**Data changes**

* Add Support model to store customizable support page content.

**Test changes**

* Add tests for support page.

v0.9.1.34 (August 02, 2020)
---------------------------

Create POA&M management as a "PAOM" Statement type inside the database instead as existing as questionnaires.

**UI changes**

* Add pages for listing, creating and editing POA&Ms.
* Add "POA&Ms" action button to project page.

**Data changes**

* Add "Poam" model in 1 to 1 relationship with "Statement" model to create POA&M object type.
* Add "uuid" field to "Statement" model to make POA&M id management easier.
* Add "uuid" to "Element" model.
* Adjust migration scripts to back-fill Element records during migration.

**Test changes**

* Add tests for Poam object.

v0.9.1.33 (August 01, 2020)
---------------------------

Fix #986 crash on loading set-type module

**Bug Fix**

* Remove an unneeded check for folder existance that was failing causing project system root_element to not be created.

v0.9.1.32 (July 26, 2020)
-------------------------

**Data changes**

* Add "part" attribute to Statement model to support tracking control implementation statements by control parts.

**UI changes**

* Add "Part" field into control implementation statement editor.

v0.9.1.31 (July 16, 2020)
-------------------------

**Bug fix**

* Fixed no route error received when Admin following a link to imputed page from task finished page (link path was not correct).

v0.9.1.30 (July 16, 2020)
-------------------------

**Bug fix**

* Case insensitive prevention of duplicate portfolio names.

v0.9.1.29 (July 10, 2020)
-------------------------

**UI changes**

* Added OSCAL to control editor.

v0.9.1.27 (July 09, 2020)
-------------------------

**UI changes**

* Added last updated information to display of selected controls.
* Admin interface replaced `parent` field on Statement model admin page with `producing_element`
* Admin interface added read-only view of dates to Statement and ElementControl model admin pages.

**Data changes**

* Added `smts_updated` field to ElementControl.
* Fixed `updated` field to automatically add update of record date to Statement, Element.
* Updated help_text on Statement `parent` field. Note that `parent` field is not being used at this time.

v0.9.1.27 (July 06, 2020)
-------------------------

**Bug changes**

* Fix invite showing as invalid on project in some cases because not checking guardian permissions.

v0.9.1.26 (June 29, 2020)
-------------------------

**Bug changes**

* Fix error assigning edit perms to system.root_element from missing path reference to root_element.
* Extend timeout on output template generation

**Miscellanous changes**

* Update README to correct aging links.

v0.9.1.25 (June 24, 2020)
-------------------------

**Feature changes**

* Include the ability to edit implementation statements and add new implementation statements for a system component on the system component view. This is nice because you manage the content associated with a component on the component page for a system.

**Deployment changes**

* Remove Python packages mondrianish, fpdf2 - no longer generating a mondrianish icon for new apps.
* Update various Python packages.

v0.9.1.24 (June 23, 2020)
-------------------------

**New features**

* Track whether a component-control status is planned, partially-implemented, implemented, etc.

v0.9.1.23 (June 23, 2020)
-------------------------

**Experimental features**

The following experimental features around OSCAL and OpenControl can be enabled through system settings on the `/admin/` page for system settings.

* Display component control information in OSCAL and OpenControl on component detail page.
* The OSCAL exports a single component in a partial OSCAL format.
* OpenControl export from a system's controls-selected page supports an export of an entire OpenControl repository for the system controls. This is still underdevelopment.

**Performance changes**

* Significantly improve speed of rendering of a system's controls-selected page by reducing time it takes to get component counts.

**Configuration changes**

* Add new system settings for enabling experimental OSCAL and OpenControl features.

**Data changes**

* Additional data added to controls/data to support 800-53 and 800-171 OpenControl export.

v0.9.1.22.16 (June 18, 2020)
----------------------------

(Version 0.9.1.22.15 subsumed into 0.9.1.22.16)

Miscellaneous fixes and corrections

**Documentation changes**

* Start 'howtos' page in docs for misc

**UI changes**

* Fixes to the control implementation statement editor:
  * Proper dynamic assignment of the control catalog key
  * Hyperlinking the component name to the component detail page for that system
  * Removing non-functioning "edit" button to change name of the component
  * Show correct catalog name in subtitle editor page
* Add datetime to implimentation statement spreadsheet export

**Developer changes**

* Remove commented out javascript function in control implementation statement editor
* Remove server file save of control export

**Data changes**

* Fix typos in NIST_SP-800-171_rev1

**Model changes**

* Sort statements by producer_element__name

v0.9.1.22.14 (June 17, 2020)
----------------------------

* Correctly create a default portfolio for a user accepting an invitation.

v0.9.1.22.13 (June 17, 2020)
----------------------------

**UI changes**

* Display component implementation statements on the System's component detail page making it easy to see to which controls a system element participates.

**Bug fixes**

* Correctly assign owner permissions to new system, new system root element when starting a new project and creating new system. Addresses #951.
* Correctly assign edit permissions to a new system and root element when non-admin user invites non-admin user. Addresses #953.
* Fix mislabeled JSON response preventing full remove deleted statement from editor.

**Doc updates**

* Adds log entries to log documentation for assigning of ower permissions and edit permissions to new system and its root element when users are added to a project.

v0.9.1.22.12 (June 14, 2020)
----------------------------

**Bug fix**

* Correctly assign owner permissions to new system, new system root element when starting a new project and creating new system. Addresses #951.
* Correctly assign edit permissions to a new system and root element when non-admin user invites non-admin user. Addresses #953.
* Fix mislabeled JSON response preventing full remove deleted statement from editor.

**Doc updates**

* Adds log entries to log documentation for assigning of ower permissions and edit permissions to new system and its root element when users are added to a project.

v0.9.1.22.12 (June 14, 2020)
----------------------------

**Bug fix**

* Dynamically determine control_catalog for SSP based on controls selected.

v0.9.1.22.11 (June 14, 2020)
----------------------------

**UI changes**

* Display component statement counts on a system's selected controls page via a custom tag to provide access to a dictionary key of impl_smts_counts created in the view for the page
* Add datetime to filename of a project's export JSON file

**Django Admin changes**

* In ProjectAdmin screen, change the organization field to a select field

v0.9.1.22.10 (June 14, 2020)
----------------------------

**Model changes**

* Add controls.Element.select_controls_oscal_ctl_ids property to generate list of selected controls oscal_ctl_ids. Enable list of selected controls in SSP.

**UI changes**

* Simplify references to compliance app version; display compliance app version number from 'version' key
* Simplify display of title of project in UI
* Display additional information about the compliance app in the project settings modal
* Stop showing project page's grid of options once number of projects exceeds 4

**Compliance app changes**

* Improve data extraction in project page and store so only use the 'version' key to get version information.

v0.9.1.22.9 (June 13, 2020)
---------------------------

**UI changes**

Improve the UI of the app-store-item info page.

* Improve visual continuity by making App info a larger version of the app info box in the store.
* Remove legacy catalog data that is not well maintained.
* Rearrange logo and add button.
* Make sure portfolio information is being maintained.
* Add a back to apps link under start button.

Also clean up presentation of footer in all pages.

v0.9.1.22.8 (June 12, 2020)
---------------------------

**Deployment fix**

* Remove conflict leading to infinite redirects when terminating SSL at a reverse proxy caused by SECURE_SSL_REDIRECT being set to `True` in `settings.py` telling Django to also redirect insecure `https` connections on the same server. Introduces optional new `secure_ssl_redirect`
  parameter setting for `local/enviornment.json` file for deployments where Django redirect should be used. See: https://github.com/GovReady/govready-q/issues/934.

# Force Django to redirect non-secure SSL connections to secure ssl connections

# NOTE: Setting to True while simultaneously using a http proxy like NGINX

# that is also redirecting can lead to infinite redirects.

# See: https://docs.djangoproject.com/en/3.0/ref/settings/#secure-ssl-redirect

# SECURE_SSL_REDIRECT is False by default.

**Documentation fix**

* Update documentation on NGINX deployments to include `$request_uri` when redirecting from port 80 to port 443.
* Update documentation to explain new `secure_ssl_redirect` parameter.

v0.9.1.22.6 (June 10, 2020)
---------------------------

**UI changes**

* Temporary links on Selected Controls page to assign baselines controls to a system. Will replace in future with automatic assignment.

**Developer changes**

* Make sure Baseline model is fully incorporated with 0.9.1.22.
* Add new route to assign baselines to system.root_element.
* Because we are still working on better extraction of data from questionnaires, create links in the Selected Control page to assign a baseline when none exists.
* Added new `assign_baseline` method to System object to assign
  controls that are part of baseline to the selected controls of
  a system root element.
* Comment out polling on the task_finished page to lower noise in log.

**Data changes**

* Correct an control_id typo in NIST 800-53 rev moderate baseline

v0.9.1.22.5 (June 09, 2020)
---------------------------

**Bug fix**

* Fix bug causing the starting of apps as answers to modules to fail. Reset start app form to pass a GET instead of a post to correctly pass question parameter to store.

v0.9.1.22.4 (June 09, 2020)
---------------------------

**UI changes**

* Added refresh icon to output documents to let user force refresh of output document. Useful for refreshing SSPs after implementation statements have changed.

v0.9.1.22.3 (June 07, 2020)
---------------------------

**Feature changes**

This version integrates the new implementation statements
stored in GovReady-Q's database into the Output Docs.

The implementation statements are accessed via a new `{{ system }}`
object. The `system` object provides access to the component-to-control
implementation statements that we began storing as distinct database
objects in version 0.9.1.5 of GovReady-Q.

The `system` object is injected into the Output Document context as
an item in guidedmodules.module_logic. NOTE: if the context from
the view already has a `system` item, it will not be overwritten.

Exactly one Information System associated with the project (if one exists).

The key attribute of `system` object is `control_implementation_as_dict`
containing a dictionary of all implementations statements and common controls
for a system.

    {
      "au-2": {
                "control_impl_smts": [smt_obj_1, smt_obj_2],
                "common_controls": [common_control_obj_1, common_control_obj_2],
                "combined_smt": "Very long text combining statements into a single string..."
              },
      "au-3": {
                "control_impl_smts": [smt_obj_3, smt_obj_4, ...],
                "common_controls": [],
                "combined_smt": "Very long text combining statements into a single string..."
              },
      ...
    }

**Documentation changes**

* Add initial documentation describing the `{{ system }}` object and the previously created `{{ control_catalog }}` object.

v0.9.1.22.2 (June 07, 2020)
---------------------------

**Deployment changes**

CRITICAL fix for deployment documentation and configuration files.

* Remove all comments from `supervisor-govready-q.conf ` because trailing "# comments" cause line to be ignored. This caused a problem in Ubuntu deployment documentation leading to a situation where gunicorn was starting in wrong context and python packages not found.
* Improved `settings.py` handling of deprecated `host` and `https` parameters for setting `SITE_ROOT_URL` value.

v0.9.1.22 (June 05, 2020)
-------------------------

**Feature changes**

Improve application logging. Add `structlog` library. Log permission escalations.
See documentation for a description of the event log formats.
The following logged events have been added:

"update_permissions portfolio assign_owner_permissions" - assign portfolio owner permissions
"update_permissions portfolio remove_owner_permissions" - remove portfolio owner permissions
"portfolio_list" - view list of portfolios
"new_portfolio" - create new portfolio
"new_portfolio assign_owner_permissions" - assign portfolio owner permissions of newly created portfolio to creator
"send_invitation portfolio assign_edit_permissions" - assign portfolio edit permissions of newly created portfolio to creator
"send_invitation project assign_edit_permissions" - assign edit permissions to a project and send invitation
"cancel_invitation" - cancel invitation to a project
"accept_invitation" - accept invitation to a project
"sso_logout" - Single Sign On logout
"project_list" - vew list of projects
"start_app" - start a questionnaire/compliance app
"new_project" - create a new project (e.g., questionnaire/compliance app that is a project)
"new_element new_system" - create a new element (e.g., system component) that represents a new system

**Deployment changes**

* Update name of git 2 CentOS package to git222 in Dockerfile.

**Documentation changes**

* Added documentation section on logging.

v0.9.1.20 (May 31, 2020)
------------------------

**Documentation changes**

* Re-wrote Ubuntu from Source instructions to explain deployment in much greater detail.
* Extend Ubuntu from Source instructions to include Gunicorn, Supervisor, and NGINX
* Created sets of exammple configuration files in ``local-examples`` to make deployment eaiser.

**Deployment changes**

* Introduce the ``govready_url`` environment parameter as a replacement for multiple params of ``host``, ``port``, and ``https``. During transition period ``govready-url`` parameter overrides any setting of ``host``, ``port``, and ``https`` parameters. Example below shows the ``local/environment.json`` file using the single ``govready-url`` parameter replacing legacy parameters:

```
    # Preferred local/environment.json file using govready-url parameter

    {
      "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
      "govready-url": "http://localhost:8000",
      "debug": false,
      "secret-key": "long_random_string_here",
      ...
    }


    # Legacy version local/environment.json file using deprecated host, https parameter

    {
       "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
       "host": "localhost:8000",
       "https": false,
       "debug": false,
       "secret-key": "long_random_string_here",
       ...
    }
```

* Created sets of exammple configuration files in ``local-examples`` to make deployment eaiser.
* The ``install-govready-q.sh`` script now reads the ``govready-url`` parameter from ``local/environment.json`` and uses the values to start GovReady-Q on the indicated host and port.

v.0.9.1.19 (June 02, 2020)
--------------------------

**UI Changes**

* Intially collapse component controls so it is easier see all components.
* Add full text of implementation statement to accordian panel header to make it easier to read controls.
* Create routes and templates for displaying components (e.g., elements) associated with a system.

v0.9.1.18 (May 30, 2020)
------------------------

**Documentation changes:**

* Ubuntu from source installation docs updated to include upgrading pip to solve problem of Ubuntu's defualt pip not installing Python packages under Linux user installs.

v0.9.1.17 (May 29, 2020)
------------------------

**UX changes:**

Performance improvements to improve rendering questions faster.

A major change in this commit is to create a cache for Jinja `expression_compile` routine.
This new cache is `jinja2_expression_compile_cache` and seems to have a noticable improvement
on maintaining a regular amount of time to render questions.

Several page reloads were the result of page redirects being handled
based on content of the next page inside the question save form. Calculating the next page
to display while accounting for skipping computed pages is now handled server side as a function
that can be called.

Removed links to imputed pages from the module finished page. It does not make sense to
link to imputed questions when users cannot visit imputed question pages.

Improve caching of OSCAL control catalogs.

v.0.9.1.16 (May 18, 2020)
-------------------------

**Development changes**

* Correct setup of tests in discussions app to avoid failing due to missing system modules.

v.0.9.1.15 (May 18, 2020)
-------------------------

**Deployment changes**

* Set gunicorn worker number to 1. Multiple gunicorn workers without SECRET_KEY set causes issue where new session key is autogenerated, sent user, and user has to constantly re-login.

v.0.9.1.14 (May 17, 2020)
-------------------------

**Deployment changes**

* Update deployment/docker/first_run.sh script to accept and pass along `--non-interactive` flag.
* Create install-govready-q.sh script (based on quickstart.sh) to have an easy single script for installing GovReady-Q.
* Update Dockerfile to copy over new install-govready-q.sh script and quickstart.sh script.
* Use docker_container_run.sh script in instructions for installing in the cloud.

**Documentation changes**

* Improvements to docker install, installation guides.
* Improve sequencing of install steps in Ubuntu. Apply improved improved squence to installing on CentOS guide.
* Breakout installation guide for Docker guides into "local", "cloud" and "advanced configuration options".

v.0.9.1.13 (May 17, 2020)
-------------------------

**Bug fixes**

* Correct control look up errors on the control catalog group page.
* Remove control lookup from catalog listing page.

v.0.9.1.12 (May 16, 2020)
-------------------------

**Deployment changes**

Gracefully handle AttributeError in siteapp migration 0030 possibly related to dangling discussion objects.

v.0.9.1.11 (May 11, 2020)
-------------------------

**Deployment changes**

Add docker compose file for deploying GovReady and Wazuh together.

v0.9.1.10 (May 10, 2020)
------------------------

**Feature changes**

Add in baselines listings for 800-53 Rev 4 (low, moderate, high) and 800-171 Rev 1.

Assigning baselines only available from Django commandline shell at momement (no UI).

**Documentation changes**

v0.9.1.9 (May 08, 2020)
-----------------------

v0.9.1.8.2 (May 10, 2020)
-------------------------

Update Documentation. Organization installation documentation inside of `Installation Guide` directory.
Clean up singe pages for installation notes on each Operating System flavor.
Rename 0.9.0 mentions to 0.9.x. Remove installation instructions from 0.9.x directory.

v0.9.1.9 (May 08, 2020)
-----------------------

Add export to Xacta Control Implementation Excel file format.

v0.9.1.8.1 (May 07, 2020)
-------------------------

Add export to Xacta Control Implementation Excel file format.
Add full draft of 800-171_rev1_catalog.json in OSCAL.

v0.9.1.8 (May 06, 2020)
-----------------------

Create new projects and systems in pairs. When a Project is created by adding a
questionnaire (e.g., compliance app) from the store, create the linked System, too.

Projects and systems are now also given a unique name via the appending of the
project's unique ID to the name.

**Developer changes**

When a root Project App object is added from the store automatically
create the Project's linked System object consisting of a Element object
and a System object with the Element as the System's root_element.

When user updates the Project name, also update the name of the
System's root_element to keep names synchronized.

In the future as the store expands, more tests might be needed to
make sure only certain top level apps are creating systems. Right now
we use the existing tests of adding a Project to the "Started Apps"
folder as indication the Project is a top level app requiring a system.

v0.9.1.7 (May 02, 2020)
-----------------------

PDF generation and thumbnails are turned off by default for
security reasons. Change PDF and custom thumbnail generation for uploaded
files to optional. Require Admins to separately install the `wkhtmltopdf` library.

PDF generator library ``wkhtmltopdf`` has security issues wherein individuals could add
HTML references such as links or file references inside the documents
they are creating which the PDF Generator blindly interprets. This leads
to SSRF (Server Side Request Forgery) in which data is retrieved from
server and added to PDF by the PDF Generator. An issue also exists
with the sub-dependency of `libxslt` before CentOS 8.x raising CVE vulnerability
with scanners. For these reasons, PDF Generation is now a configurable setting.

v0.9.1.6 (April 29, 2020)
-------------------------

Continue to improve control editor.

Enforce unique Name field on Element model.
Match Component (Producer Element) by unique name to existing
Producer Element in the database when creating a new Statement.

Improve the combining of component statements.
Temporarily put result into a textarea to make easier to copy manually.

v0.9.1.5 (April 21, 2020)
-------------------------

Build on control catalog search to begin to represent
controls in the database for each system.

Control Guidance using OSCAL (#833)

* Small metadata changes to models
* Add 800-53 control catalog to output templates

First effort to add control catalogs (e.g., control guidance)
to the output templates using OSCAL and to create an editor
for adding and editing control statements stored in the database.

Initial user story is as a user/developer wanting to import
a spreadsheet of common controls to have a better interface for
reading the common controls against the control statement and
drafting the application layer controls for hybrid controls.
The user wants an easier way to do this than a spreadsheet because
spreadsheets are hard to read.

Begin a parser library to have code to input variously formatted
source material into the database.

** Developer changes **

Replace SecControl library and parsing older XML version
of 800-53 catalog with pure python parsing of modern
OSCAL version of catalogs.

We also add a new item type to module_logic.TemplateContext called
`control_catalog`. When includeing `{{control_catalog}}` in output
template we now have access to a dictionary of controls where
each control is listed as a dictionary.

Create a new script `oscal.py` and a `Catalog` class
and create look ups of controls.

Because OSCAL is hierarchical and recursive, we also generate
a flattened, simplified version of our control catalog.

* Add simple CommonControl model

Add simple CommonControl and CommonControlProvider models.

We are creating CommonControl model as first step to being able
to manage control implementation statements in GovReady.

We also want a way to import CommonControls into GovReady database.

We create `CliControlImporter` as first cut tool for reading
an excel spreadsheet with xlrd, converting the rows to simple
control object and importing into the database. Code snippets
included. Class and snippets only work for one spreadsheet format,
but some abstraction exists to make customization easier for other
formats.

Refactor implementation editor to use panels and have
interactivity for adding additional implementation statements
using Boostrap 3.3. panel model.

In models, sketch out the "statement" model for implementation attestations
but leave commented out for present.

Add Ajax calls to save implementation statements

This commit puts in the Django and Javascript to save a statement
to the server via Ajax.

Each implementation statement panel and form is given a unique id
when added to the page to make sure the correct statment information
is passed to the server.

When component name is updated, the panel title updates.

Add hidden fields to send the control id and the system name as part
of the form.

[WIP] Add utility class to parse statements with tagged elements

Create utility `StatementParser_TaggedTextWithElementsInBrackets` class
to parse collection of statements in a text file with serially listed
controls where control ids and elements are enclosed in brackets.

The idea is that common controls or other controls can be extracted
and put into a long text file separated by control ids. Brackets are put around
proper entities (e.g., system "elements") that mentioned in the implementation
statement. By identifying system elements, it is possible to build a basic
entity identification tool and create a specific listing of elements involved
in each implementation statement. This is an initial step to create
component-to-control mappings.

* Goal is to save statement of whatever length and list of system elements
  involved with process
* Ignore multiple intervening lines
* System name must be entered manually
* Script makes one pass to build search dictionary with bracketed strings
  then uses dictionary to find all instances of strings in statements.
  This makes it unnecessary to place all instances of elements regardless of brackets.

Like other parse and import utility classes, this basic code may need modifications
for specific situations.

* Add Statement, Element models; Save implementation statements

This commits finishes work started in commit 4e77ba531069832d0a2507ebfd32a0e41f2bf8df

This commit adds Statement and Element models as the core feature
to track component-to-control statements. The more general terms of
"Statement" and "Element" are used instead of "Control"and "Component".

An "implementation statement" is a statement (and attestation).

A many to many relationship is supported for Statements and Elements.

This commit finishes in the Django and Javascript to save a statement
to the server via Ajax.

To Do:

- Delete statements
- Tests written

v0.9.1.4 (April 08, 2020)
-------------------------

This release exposes control catalog to end users for search.

Previously versions embedded controls within output templates.

**UI changes**

* Create new `control` pages for looking up control catalog guidance.

**Developer changes**

* Add 800-53 control catalog via classes `SecControlsAll` and `SecControl`
* Create a new directory `controls` into which we add a class for listing a security control catalog.
* Add a new item type to module_logic.TemplateContext called `control_catalog` to enable iterable dictionary of control catalog.

v0.9.1.3.3 (April 07, 2020)
---------------------------

**Deployment changes**

* Remove build gcc-c build lib from build
* Remove uwsgi from requrirements
* Refactor Dockerfile for clarity
* Upgrade to Django 2.2.12 LTS to address issue noted by pyup.io safety
* Update various Python libraries

**Bug fixes**

* Fixed issue where only users who could use the editing tool could see the datagrid questions render

v0.9.1.3.1 (March 31, 2020)
---------------------------

**UI changes**

* Add `render` key to datagrid question type to force vertical rendering of tabular data

v0.9.1.3 (March 25, 2020)
-------------------------

**Deployment changes**

* Upgrade requirements

**Bug fixes**

* Gracefully handle empty datagrid question type in output templates

v0.9.1.1 (March 20, 2020)
-------------------------

**UI changes**

* Conditionally add in route `accounts/logout` when SSO Proxy enabled.

v0.9.1 (March 12, 2020)
-----------------------

GovReady-Q now supports Datagrid question type for easy entry of tabular data.

**UI changes**

* Use datagrid (jsGrid) to support questions best answered with tabular data.

v0.9.0.3.3 (February 23, 2020)
------------------------------

**Bug fixes**

* Use Math.pow in main.js to fix IE11 failing to display invite modal

v0.9.0.3.2 (February 21, 2020)
------------------------------

**Deployment changes**

* Support environmental param for GovReady Admins in SSO context
* Create portfolio for user account added by SSO
* Adding in views.debug route and view
* Remove deprecated upgrade app view

**UI changes**

* Fix IE11 not displaying assign and invite modals due to error parsing main.js

**Other changes**

* Add templates for Django performance debug toolbar

v0.9.0.3 (November 21, 2019)
----------------------------

**UX changes**

* Significantly improve performance of rendering questions and module review page (PR #774)
* Fix failure to display list of questions in progress history in certain circumstances

**Developer changes**

* Create migrations for shortening varchar field length to 255 on siteapp.models

**Deployment changes**

* Adding in health paths to examine static files.

v0.9.0.2 (October 16, 2019)
---------------------------

Minor patches to v0.9.0.

**UX changes**

* Permissions added to settings modal. Permissions removed from settings. (#761)
* Correctly display database type SQLite on /settings (#764)

**Documentation changes**

* Minor typo corrections. (#762)

v0.9.0 (October 9, 2019)
------------------------

Our most exciting release of GovReady-Q!

* Faster loading and launching of asssessments/questionnaires!
* Simplified install with no subdomains to worry about!
* Better permissions model using Django-Guardian!
* Portfolios to organize projects and manage permissions and access!
* Better authoring tools!
* Streamlined new register,login page!
* Beautiful and helpful new start page!
* One-click deployment scripts for simple testing deployments into AWS.

**WARNING - SIGNIFICANT DATABASE CHANGES**

Running the migrations to update the database will perform changes that will prevent rolling back the data migrations.

**Migrating from 0.8.6 to 0.9.0**

We recommend testing 0.9.0 with an empty database.

We recommend testing migrations from 0.8.6 to 0.9.0 against a copy of your database.

We have developed migration script and guide to support 0.8.6 to 0.9.0 upgrades.

New manage.py commands help populate 0.8.6 test data to test migration scripts.

**Security enhancements**

* Upgrade to Django 2.2.x to address multiple security vulnerabilities in Django prior to 2.2.

**Catalog changes**

* Compliance apps catalog (blank projects/assessments) read from the database rather than going to remote repositories App Source. Performance significantly improved.
* Delete app catalog cache because the page loads fast.
* New versions of the compliance apps are added to the catalog at the bottom of the Guidedmodules > AppSource page in the Django admin interface.

**Multitenancy and subdomains removed**

* Remove multitenancy and subdomains.
* Serve all pages on the same domain.
* Remove organization-specific name and branding from nav bar.
* Projects page now shows projects across all of a user's organizations, various functions that returned resources specific to an organization don't filter by organization.
* Single apps catalog for all users. (In future we will use new permissions model to restrict access to compliance apps in catalog.)
* [WIP] Remove link to legacy organization project in settings page.

**Portfolios added**

* Portfolio feature to organize and manage related projects (assessments).
* Projects exist in only one portfolio.
* [WIP] When a new user joins GovReady they are automatically added and made owner of their own Portfolio.
* Any user can create a portfolio and add projects to the portfolio.
* Users can be invited to a Portfolio by Portfolio owners and granted ownership by Portfolio owners.

**Permission changes**

* Added popular, mature Django-Guardian permission framework to enable better management of permissions on indivdidual instances of objects.
* New Permissions object primarily applied to portfolios in this release, with some overlap into projects.
* Preserved original lifecycle interface in template project_lifecycle_original.html.
* On login errors make signin tab active on page reload to display the errors.
* Remove listing in catalog of the fields related to the size of the organization.
* Display username instead of email address for user string.
* Use plane language for names of top-level questionnaire stage columns: To Do, In Progress, Submitted, Approved.

**Authoring tool improvements**

* Superusers can create whole new questionnaire files.
* Edit question modular dialog moved from large center screen popup to right-hand sidebar.
* Increase readability of edit form.
* Insert question into questionnaire.
* Enable editing on questionnaires from all App Sources instead of just "local".
* Button to view entire questionnaire source YAML.
* TEMPORARY correction of admin access to get tests to run. MUST FIX.
* Upgrade assessment no longer requires loading intermediary page; Upgrade routine begins directly with action button.

**UX changes**

* Clean up reactive styling to operate across multi-size screens.
* Register/login page simplified by putting register and sign in inside a tabs and replacing jumbotron look and feel with minimal sign up and join links.
* User home /project page improved with four getting started actions recommend on what was previously a nearly blank page; replacing "compliance app" terminology with "project" terminology; sleeker table-like display of started projects.
* Question progress list improved styling incorporates colors to more clearly see completed and skipped questions and displays module to module progress.
* Question navigation to next question now linear to make skipping around easier and links to question in next module.
* Nav bar provides "add" button to start new project or create portfolio from every appropriate page.
* Nav bar improved with displayed links to "Projects" and "Portfolios".
* Nav bar icons for "Analytics" and "Settings"; Remove of dropdown "MENU" item.
* Django messages indicating successful logins/logouts now ignored in base template. Change will hide any Django message of level "Success". Hiding success messages removes the need to dismiss messages or fade them out.

**Developer changes**

*Organization related*

* The OrganizationSubdomainMiddleware which checked the subdomain in the request host header, performed Organization-level authorization checks, and set the global request.organization attribute to the requested Organization, is deleted.
* the Content Security Policy for the site is updated to remove the white-listed landing domain (we used it for cross-origin requests to get user profile photos, which were always served from the landing domain)
* Django's ALLOWED_HOSTS setting no longer needs an entry for a wildcard subdomain under the landing domain since we are not using that anymore.
* The LANDING_DOMAIN, ORGANIZATION_PARENT_DOMAIN, SINGLE_ORGANIZATION_KEY, and REVEAL_ORGS_TO_ANON_USERS attributes on django.conf.settings are removed.
* Update tests for organizational removal.
* Remove description of multi-tenant mode and organization subdomains from documentation.
* siteapp.views.new_folder isn't currently in use, so did not fully update related code to get the new folder's organization from somewhere.
* Starting to switching language from apps to assessments/questionnaires.
* Beware of legacy references to organization in source code. Still cleaning up removal of multitenancy and subdomains.
* Absolute URLs to user-uploaded media now use SITE_ROOT_URL instead of organization subdomains.
* The landing domain URLs are moved into the main urlconf (except the ones that were duplicated in both urlconfs because they appeared on both domains).
* Revise API URLs to no longer have the organization in the path (we can put it back if it was nice, but it no longer serves a functional purpose).
* Remove the Invitation.organization field.

*Questionnaire related*

* AppVersion now has a boolean field for whether the instance should be included in the compliance apps catalog for users to start new projects with that app.
* The AppSource admin now lists all of the apps provided by the source and has links to import new app versions into the database and to see the app versions already in the database by version number.
* When starting a compliance app (i.e. creating a new project), we no longer have to import the app from the remote repository --- instead, we create a new Project and set its root_task to point to a Module in an AppVersion already in the database.
* App loading is refactored in a few places. The routines for getting app catalog information from the remote app data are removed since now we only need it for apps already stored in the database.
* The AppSource admin's approved app lists form is removed since adding apps into the database is now an administrative function and the database column for it is dropped.
* Tests now load into the database the apps they need.
* The app catalog cache is removed since the page loads much faster.
* User profile information was previously pre-loaded by the OrganizationSubdomainMiddleware, now it's loaded on first use.
* When users register, the email to site admins no longer includes the organization they were looking at when they signed up because there's no such thing anymore.
* Fix tests to login with new forms in landing page tabs

*Miscellaneous*

* Fix various SonarQube reported issues to use preferred HTML tags for stong and em
* Testmocking scripts for populating test data into application.

**Deployment changes**

* Remove multi-tenancy and serves all pages from the on the same domain. Previosuly, requests to Q came in on subdomains and the subdomain determined which Organization in the database the request would be associated with and individuals had to re-login across subdomains. Multitenancy increased install complexity and we were not seeing use of the multitenancy feature. Deployment is now simpler.
* Add deployment scripts of multi-container GovReady-Q and NGINX via Docker-compose.
* Prevent multiple notification emails in environments running multiple Q instances against single database by performing record lock on notification and checking if notification already sent.
* `first_run` reports if Superuser previously created.
* Added check to `dockerfile_exec.sh` to prevent unintended 0.9.0 databse upgrades.

v0.8.6.2+devel
--------------

* The AppInstance model/database table was renamed to AppVersion to better reflect the meaning of the model.
* Upgraded some dependencies.

v0.8.6.2 (August 14, 2019)
--------------------------

Development/testing changes:

* Added `quickstart.sh` script for quick install and testing with mock data.
* Added mock data generation for testing.

Documentation changes:

* Tabbed docs.
* Improvements in documentation.

v0.8.6.1 (May 08, 2019)
-----------------------

Deployment changes:

* [Fix] Modified Dockerfile to build MySQL-related libraries into Docker deployment so container would support using MySQL databases out of the box.

v0.8.6 (April 29, 2019)
-----------------------

Application changes:

* Removed "I'll Come Back" and "Unsure" skip buttons that were confusing users. (Data structures retained in database for backward compatability and for possible improved version of indicators.)
* Organization Administrators can now be added within organization Settings by other Organization Administrators.
* Project (e.g., Compliance App) administrators can now be added within Apps settings.
* @ mention any user within discussion regardless of organization or project member instead of @ mentioning only users within the project.
* The compliance apps catalog is now read from compliance apps cached in the database rather than querying local and remote AppSources each time the catalog is loaded or an app is started. A new field is added to the AppVersion (formerly AppInstance) model in the database for whether it should be included in the compliance apps catalog. The AppSource admin's approved apps list table is replaced with a new table showing which compliance apps from the source are already in the compliance apps catalog (or hidden from the catalog but in the database) and which which can be added.

Developer changes:

* Expose rich question metadata within output document templates. Documents can now access if question was skipped by user and skip reason, if question was answered or not, if answer imputed and other goodies.
* Compliance App authors can now remove the skip buttons from displaying on questions by indicating them hidden in the App's `app.yaml` file.

Documentation changes:

* Clearer system requirements discussion.
* Fixed a mis-matched heading in documentation that was causing generated hierarchial table of contents to be malformed.
* Reflowed documentation sections to put deployment instructions earlier and improved structure of deployment instructions.
* Test documentation now includes examples for running individual test Classes and methods.

Deployment changes:

* Split off MySQL-related libraries into a separate pip requirements file so `mysql-config` library would only be required when installing Q with MySQL.
* Upgraded  dependencies.
* The AppInstance model/database table was renamed to AppVersion to better reflect the meaning of the model.
* Upgraded some dependencies.

v0.8.5 (February 9, 2019)
-------------------------

Application changes:

* An undocumented feature called "unskippable questions" was removed. This feature inadvertently hid some questions, resulting in a module being indicated as finished but its progress bar showing questions are unfinished.

Deployment changes:

* GovReady-Q can now be deployed behind an enterprise reverse proxy authentication server that sends login information in HTTP headers.
* Python 3.6+ is now required.
* Documentation was added for creating a custom Docker image that adds organization branding to the site.

Developer changes:

* Add a new VERSION file to source code control that stores the current version of the software, plus a commit hash for public releases, so that nightly builds don't fail because of a missing VERSION file. Add build tests to ensure the VERSION file matches the top release in CHANGELOG.md and ends with "+devel" if and only if this is a development release.
* The application was not working on macOS in version v0.8.4 because of a bug in commonmark 0.8.0.
* Some of the templates were split out into multiple files to make it easier to override them for custom branding.
* Upgraded some dependencies.

v0.8.4 (October 23, 2018)
-------------------------

Application changes:

* "Invite Colleague" on the home page now is always displayed instead of being hidden in some cases.
* The "Related Controls" button on project pages is back now as "Documents."

App authoring changes:

* Output document templates can now be stored in separate files rather than all output document templates being stored in the module YAML file.

Other changes:

* A new command-line tool called "assemble" is available that instantiates an entire project from a YAML file of app selections and question answers and generates/saves output documents to files on disk.
* Add system minimum and recommended software requirements to documentation.
* Version 0.8.3 skipped.

Developer changes:

* Non-cryptographic hash functions replace cryptographic hash functions in places where a cryptographic hash function is not necessary and might be excessively slow.
* Other minor fixes.
* Upgraded some dependencies.

v0.8.2 (July 20, 2018)
----------------------

Application changes:

* Javascript and CSS static assets of compliance apps may have had the wrong MIME type set.

App authoring changes:

* The authoring tool is updated to show app catalog and other app-module YAML in two textareas instead of one, since they are now stored separately in the database (see below), but they are recombined when the authoring tool updates local files.
* A new `version-name` field is added to app.yaml catalog information.

Deployment changes:

* The HTTP Content-Security-Policy header is now set to prevent browsers from loading any third-party assets.
* A CentOS 7-based Vagrantfile has been added to the source distribution for those looking to deploy using a VM.
* Added some outputs to Docker launches to see the Q version and the container user during build and at the very start of container startup.
* We're now publishing version tags to Docker Hub so that past versions of GovReady-Q remain available when we publish a new release.
* With Docker, email environment variable settings were ignored since the last (-rc3) release.

Developer changes:

* The AppInstance table now has created and updated datetime columns, version_number and version_name columns extracted from the catalog metadata, and a new catalog_metadata field that holds the original YAML 'catalog' information (but in JSON in the database; this information was previously in the 'app' Module's spec field).
* The ModuleAssetPack table is dropped and its columns have been moved to the AppInstance table.
* Code refactoring: split module_sources.py into two modules.
* Upgraded some dependencies.

v0.8.2-rc3 (May 18, 2018)
-------------------------

Application changes:

* Apps can now be upgraded by project administrators.
* Project administrators can now delete tasks.
* Emojis are now served using static assets and an emoji-related IE11 incompatibiltiy was fixed.
* Performance improvements.
* Minor UI improvements.
* Minor bug fixes.

App authoring changes:

* Apps can now have a README.md file which is displayed in the app's catalog page, replacing the catalog long description field.
* Templates now allow multi-line Jinja2 directives.
* Template errors now show line numbers.

API changes:

* module-set questions can now be created through the API.

Administrative changes:

* Minor bug fixes.

Deployment changes:

* Documentation is now published at http://govready-q.readthedocs.io/en/latest/.
* Docker launch failed if `HTTPS` environment variable was not passed in and may have failed with a permission denied error and now gives a better error message when the database cannot be created on a read-only filesystem.
* Docker deployments now support environment variables for all application settings.
  opened, such as if we're in a Docker container with a read-only filesystem, and documentation improved.
* Added a new `branding` environment setting for sites to override templates and provide new assets using a custom Django app, and improved our Dockerfile to make it easier for downstream packagers to incorporate into their own images.
* Added HTTP->HTTPS redirects in Docker deployments using HTTPS that also respond to HTTP requests.
* Updated documentation for App Sources and RHEL deployments.
* Added preliminary documentation for deplying to Amazon Web Services Elastic Container Service.

Developer changes:

* Docker builds now run `yum update`, install a MySQL database driver, and run Django checks.
* Improved the test_screenshots management command to help creating screencasts.
* Dropped dependency licensing checking.
* Upgraded some dependencies.

v0.8.2-rc2 (April 12, 2018)
---------------------------

Application changes:

* Downloading output documents in 'markdown' format no longer round-trips through pandoc when the template was authored as Markdown.
* Fix caching bug with output documents in multiple formats.
* Small UI improvements.

App authoring changes:

* Templates no longer die when an undefined variable is accessed but instead show inline error messages.

Deployment changes:

* Docker launch failed if some environment variables were not passed in.

Developer changes:

* Docker image build script now pulls the latest CentOS image before building and checks that a CHANGELOG entry has been added for the release version.
* Changelog entries added for recent past releases.
* Upgraded some dependencies.

v0.8.2-rc1 (April 9, 2018)
--------------------------

Administrative changes:

* Send site admins an email whenever a user signs up or an organization is created.

Deployment changes:

* Docker now uses uWSGI as the production-grade HTTP+application server instead of `manage.py runserver`.
* Docker now uses supervisord to run the application server and the notification emails background process, which had not been running in Docker deployments.
* Our Docker first_run script was broken by a recent release.

v0.8.1 (April 9, 2018)
----------------------

Application changes:

* Replace the "Skip" button with I don't know, It doesn't apply, I'll come back, and Not sure.
* Minor UI improvements.

v0.8.0: v0.8.0-rc0 (Feb. 27, 2018) through v0.8.0-rc13 (April 6, 2018)
----------------------------------------------------------------------

Application changes:

* The homepage listing projects and folders has been revamped to lay out compliance projects in lifecycle stage columns.
* Project pages now arrange tasks in columns as well according to the completion status of the task, tasks have progress bars showing completion, and module-set questions with multiple answers are now shown as separate entries.
* On the review page, the reviewed state of questions can now be changed with one click.
* Discussion comments are now entered using a plain text editor instead of a rich text editor, and @-mention autocompletes are working again.
* Added a button to clear the compliance apps catalog cache to the bottom of the app catalog page that only users with the Django appsource_change permission can see.
* Added various error handling for invalid app content and invalid AppSource configurations.
* Tasks whose titles are automatically set by rendering the instance-name field now revert back to the module title string if the instance-name field refers to a question that has not yet been answered.
* Project import now has a better UI for its results page.
* Some performance improvements.
* Minor UI fixes and improvements.
* Fixed a bug in project import with invalid data.
* Fixed crash related to discussion guests on dangling discussions.

Administrative changes:

* Add a new settings page for administrative functions including setting up the help squad and reviewers and listing organization administrators.
* Improved the AppSource admin page to clarify setting up public and private git repositories.
* AppSources can now control which apps are shown in the catalog.
* AppSources for git repositories now use the repository's default branch instead of "master," since it might not be "master," if a branch is not specified.

App authoring changes:

* Improved the app authoring tools.
* Add a new management command for taking screenshots of starting a compliance app and answering its questions to make documentation writing easier.
* Added an 'examples' field to questions for showing example answers on question pages.
* Added 'display: top' option to output documents to show the document at the top of the task finished page.
* Apps can now be hidden by AppSource repositories using a catalog.yaml file.
* The ephemeral encryption feature was removed.
* The "required" field on questions was removed.
* The "tab" field on questions was removed.
* The "external-function" question type was removed.
* Updated documentation screenshots.

Deployment changes:

* Docker deployments now run the container's CMD process as a non-root user.
* Docker deployments now support running with a read-only root filesystem.
* Docker containers wouldn't start if FIRST_RUN wasn't set.
* Docker image now uses CentOS 7 rather than Debian.
* Docker deployments now have more logging.
* MySQL databases are now supported.
* Various other fixes for Docker.

Development changes:

* Add static code analysis testing in CircleCI using bandit.
* Added code coverage artifact to CircleCI builds.
* Upgraded our CircleCI CI pipeline to CircleCI 2.0.
* Added ability to run unit tests within the Docker deployment container.
* Replaced hard-coded test passwords with randomly generated strings.
* Small changes to avoid false positives in static code scanning.
* Improvements to the Docker launch scripts.
* Added some tests. Minor changes to tests.
* Upgraded to the Django 2.0.3 framework.
* Upgraded and pinned some dependencies.
* Documentation improvemnts.
* The installation of psycopg2 in the Dockerfile is now in requirements.txt so its hashes are checked when downloaded.

v0.7.0-rc2 (January 8, 2018)
----------------------------

First release.
