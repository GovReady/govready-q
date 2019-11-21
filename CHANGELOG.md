GovReady-Q Release Notes
========================

v0.9.0.2.5.2 (November 21, 2019)
--------------------------------

**Deployment changes:**

Adding in health paths to examine static files.

v0.9.0.2.5 (November 14, 2019)
------------------------------

Re-fetch and collect static files.

v0.9.0.2.4 (November 13, 2019)
-----------------------------

Created a Dockerfile.mesosphere to have a local build/test of container for Mesosphere to test.

v0.9.0.2.3 (November 8, 2019)
-----------------------------

For Mesosphere deployment, fetch and pre-collect the static files into `static_root`.
Make sure vendor and siteapp/static/vendor files are no longer gitignored.

v0.9.0.2.2 (November 7, 2019)
-----------------------------

For Mesosphere deployment, fetch and pre-collect the static files into `static_root`.

v0.9.0.2.1.1 (October 24, 2019)
-------------------------------

**Developer Change**

* Create migrations for shortening varchar field length to 255 on siteapp.models

v0.9.0.2.1 (October 18, 2019)
-----------------------------

Modifications to container deployment environmental variables to better support deployments in Mesosphere and other Docker orchestration environments.

**WARNING - CONTAINER ENVIRONMENTAL VARIABLE CHANGES**

The `HOST` and `PORT` container deployment environmental variables renamed to `GR_HOST` and `GR_PORT`. Update your container-based deployment configurations accordingly.

**Developer changes:**

* Change `HOST` and `PORT` container deployment environmental variable names to avoid name collision. Update container-based deployment configurations accordingly.

**Documentation changes:**

* Change `HOST` and `PORT` container deployment environmental variable names to avoid name collision in Mesosphere and other container orchestration tools.

v0.9.0.2 (October 16, 2019)
---------------------------

Minor patches to v0.9.0.

**UX changes:**

* Permissions added to settings modal. Permissions removed from settings. (#761)
* Correctly display database type SQLite on /settings (#764)

**Documentation changes:**

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

**Security enhancements:**

* Upgrade to Django 2.2.x to address multiple security vulnerabilities in Django prior to 2.2.

**Catalog changes:**

* Compliance apps catalog (blank projects/assessments) read from the database rather than going to remote repositories App Source. Performance significantly improved.
* Delete app catalog cache because the page loads fast.
* New versions of the compliance apps are added to the catalog at the bottom of the Guidedmodules > AppSource page in the Django admin interface.

**Multitenancy and subdomains removed:**

* Remove multitenancy and subdomains.
* Serve all pages on the same domain.
* Remove organization-specific name and branding from nav bar.
* Projects page now shows projects across all of a user's organizations, various functions that returned resources specific to an organization don't filter by organization.
* Single apps catalog for all users. (In future we will use new permissions model to restrict access to compliance apps in catalog.)
* [WIP] Remove link to legacy organization project in settings page.

**Portfolios added:**

* Portfolio feature to organize and manage related projects (assessments).
* Projects exist in only one portfolio.
* [WIP] When a new user joins GovReady they are automatically added and made owner of their own Portfolio.
* Any user can create a portfolio and add projects to the portfolio.
* Users can be invited to a Portfolio by Portfolio owners and granted ownership by Portfolio owners.

**Permission changes:**

* Added popular, mature Django-Guardian permission framework to enable better management of permissions on indivdidual instances of objects.
* New Permissions object primarily applied to portfolios in this release, with some overlap into projects.
* Preserved original lifecycle interface in template project_lifecycle_original.html.
* On login errors make signin tab active on page reload to display the errors.
* Remove listing in catalog of the fields related to the size of the organization.
* Display username instead of email address for user string.
* Use plane language for names of top-level questionnaire stage columns: To Do, In Progress, Submitted, Approved.

**Authoring tool improvements:**

* Superusers can create whole new questionnaire files.
* Edit question modular dialog moved from large center screen popup to right-hand sidebar.
* Increase readability of edit form.
* Insert question into questionnaire.
* Enable editing on questionnaires from all App Sources instead of just "local".
* Button to view entire questionnaire source YAML.
* TEMPORARY correction of admin access to get tests to run. MUST FIX.
* Upgrade assessment no longer requires loading intermediary page; Upgrade routine begins directly with action button.

**UX changes:**

* Clean up reactive styling to operate across multi-size screens.
* Register/login page simplified by putting register and sign in inside a tabs and replacing jumbotron look and feel with minimal sign up and join links.
* User home /project page improved with four getting started actions recommend on what was previously a nearly blank page; replacing "compliance app" terminology with "project" terminology; sleeker table-like display of started projects.
* Question progress list improved styling incorporates colors to more clearly see completed and skipped questions and displays module to module progress.
* Question navigation to next question now linear to make skipping around easier and links to question in next module.
* Nav bar provides "add" button to start new project or create portfolio from every appropriate page.
* Nav bar improved with displayed links to "Projects" and "Portfolios".
* Nav bar icons for "Analytics" and "Settings"; Remove of dropdown "MENU" item.
* Django messages indicating successful logins/logouts now ignored in base template. Change will hide any Django message of level "Success". Hiding success messages removes the need to dismiss messages or fade them out.

**Developer changes:**

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

**Deployment changes:**

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
-----------------------

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

*  The authoring tool is updated to show app catalog and other app-module YAML in two textareas instead of one, since they are now stored separately in the database (see below), but they are recombined when the authoring tool updates local files.
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
