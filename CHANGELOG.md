GovReady-Q Release Notes
========================

v0.9.0.rc.002+devel
-------------------

MAJOR version upgrade with braking database changes.

Backup your database before running these migrations.

This is our most exciting release of GovReady-Q!

* Faster loading and launching of Asssessments/questionnaires!
* Simplified install with no subdomains to worry about!
* Replaces subdomain multi-tenancy with simplified "Groups" model!
* Improved authoring tools!
* Streamlined new register,login page!
* Beautiful and helpful new start page!

NOTE: Running the migrations to update the database will perform significant changes to your data that will prevent rolling back the data migrations.

WIP CHECKLIST

- [ ] Updated documentation
- [ ] Updated tests and test passing
- [ ] Updated changelog and version number

Application changes:

* compliance apps catalog now reads from the database rather than going to remote repositories
The app catalog cache is removed since the page loads much faster.

* Remove multitenancy and subdomains Major UX improvements and convert organizations into groups All pages are served on the same domain.
* Nav bar no longer shows the current organization since pages are no longer organization-specific
* the page at /, when the user is logged out, now shows the old landing domain's homepage instead of the organization-specific homepage, but links around org names (when logged in) are removed because orgs no longer have landing pages
* the projects page now shows projects across all of a user's organizations, various functions that returned resources specific to an organization now don't filter by organization
* the apps catalog, which was organization-specific, now merges the catalogs all all of the organizations that the user is nominally a part of
* if the user is a part of more than one group, the user must choose which group to start an app in 
* Register/login page simplified by putting register and sign in inside a tabs and replacing jumbotron look and feel with minimal sign up and join links.
* User home /project page improved with four getting started actions recommend on what was previously a nearly blank page; replacing "compliance app" terminology with "project" terminology; sleeker table-like display of started projects.
* "Groups" feature to organize and manage related projects (assessments). Goal is to eventually completely replace the previous multi-tenancy Organization feature with a more informal and flexible "Groups" feature. UI uses "groups" terminology while code base currently uses "org_group" terminology to ease transition. Any user can create a group. Group names are global across a GovReady-Q install. Groups provides a folder-like functionality for organizing related projects.
* Navbar improved with displayed links to "Projects" and "Groups"; icons for "Analytics" and "Settings"; removal of dropdown "MENU" item.
* Django messages indicating successful logins/logouts now ignored in base template. Change will hide any Django message of level "Success". Hiding success messages removes the need to dismiss messages or fade them out.
* Preserved original lifecycle interface in template project_lifecycle_original.html
* Create a default org_group slug for user that is username. Test proposed slugs based on username properly report error on name collision with existing org_groups (e.g., a username cannot be created that conflicts with an existing org_group (may want to white list creating of org_groups that are common first names).
* On login errors make signin tab active on page reload to display the errors.

* Add group slug to breadcrumbs for projects, tasks and reduce font size of breadcrumbs. Add group slug to display of project name for clarity. Remove "Component" from breadcrumbs.
* Remove link to legacy organization project in settings page.
* Display username instead of email asddress for user string.
* Use plane lane language for names of top-level questionnaire stage
    columns: To Do, In Progress, Submitted, Approved.
* Start to improve authoring tool:
    - Shift question edit modular dialog from large center screen popup
      to right-hand thin sidebar and increase readability of form
    TEMPORARY correction of admin access to get tests to run. MUST FIX

Developer changes:

* All apps
* switching language from apps to assessments/questionnaires
* still legacy refrences to organization in source code. org_group language in source code.

* absolute URLs to user-uploaded media now use SITE_ROOT_URL instead of organization subdomains
* the landing domain URLs are moved into the main urlconf (except the ones that were duplicated in both urlconfs because they appeared on both domains)
* revise API URLs to no longer have the organization in the path (we can put it back if it was nice, but it no longer serves a functional purpose)

* AppVersion now has a boolean field for whether the instance should be included in the compliance apps catalog for users to start new projects with that app.
* The AppSource admin now lists all of the apps provided by the source and has links to import new app versions into the database and to see the app versions already in the database by version number.
* When starting a compliance app (i.e. creating a new project), we no longer have to import the app from the remote repository --- instead, we create a new Project and set its root_task to point to a Module in an AppVersion already in the database.
* App loading is refactored in a few places. The routines for getting app catalog information from the remote app data are removed since now we only need it for apps already stored in the database.
* The AppSource admin's approved app lists form is removed since adding apps into the database is now an administrative function and the database column for it is dropped.
* Tests now load into the database the apps they need.
* The app catalog cache is removed since the page loads much faster.

* Organizations now have 'slug' instead of 'subdomain'. get_absolute_url is removed because Organizations have no dedicated pages on the site. get_url is removed because we no longer need complicated logic to form the right absolute URLs to Organization page, since there is no such thing as Organization-specific pages anymore
* remove the Invitation.organization field
* User profile information was previously pre-loaded by the OrganizationSubdomainMiddleware, now it's loaded on first use
* when users register, the email to site admins no longer includes the organization they were looking at when they signed up because there's no such thing anymore
* siteapp.views.new_folder isn't currently in use, so I didn't fully update it to get the new folder's organization from somewhere
* update tests
* remove description of multi-tenant mode and organization subdomains from documentation

* the OrganizationSubdomainMiddleware which checked the subdomain in the request host header, performed Organization-level authorization checks, and set the global request.organization attribute to the requested Organization, is deleted
* the Content Security Policy for the site is updated to remove the white-listed landing domain (we used it for cross-origin requests to get user profile photos, which were always served from the landing domain)
* Django's ALLOWED_HOSTS setting no longer needs an entry for a wildcard subdomain under the landing domain since we are not using that anymore
* the LANDING_DOMAIN, ORGANIZATION_PARENT_DOMAIN, SINGLE_ORGANIZATION_KEY, and REVEAL_ORGS_TO_ANON_USERS attributes on django.conf.settings are removed

* Fix tests to login with new forms in landing page tabs

Deployment changes:

* Removes multi-tenancy and serves all pages from the on the same domain. Previosuly, requests to Q came in on subdomains and the subdomain determined which Organization in the database the request would be associated with and individuals had to re-login across subdomains. Multitenancy increased install complexity and we were not seeing use of the multitenancy feature. Deployment is now simpler.


v0.8.6.2+devel
--------------
* The AppInstance model/database table was renamed to AppVersion to better reflect the meaning of the model.
* Upgraded some dependencies.


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
