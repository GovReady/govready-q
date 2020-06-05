GovReady-Q Release Notes
========================

## v0.8.6.5.2 (June 5, 2020)

Update Dockerfile to use repo https://repo.ius.io/ius-release-el7.rpm
and install `git222`.

Update Dockerfile to remove safety check on Python repos because we have
some older repos currently that need updating, including Django.

## v0.8.6.5.1 (June 5, 2020)

Back port fix to address bug in guidedmodules/admin.py appearing after moving to Python 3.
This the PR #811 applied to 0.8.6.5.

## v0.8.6.5 (May 3, 2020)

Better jinja2_expression_compile_cache and next-page redirect

This commit is a back port of performance improvements in 0.9.x to 0.8.6.

This performance improvement commit creates a cache for Jinja `expression_compile` routine.
This new cache is `jinja2_expression_compile_cache` and seems to have a noticable improvement
on maintaining a regular amount of time to render questions.

Also addressed are several page reloads that were the result of page redirects being handled
based through interactions with the browser based content of the next page inside the question
save form. Calculating the next page to display, which accounts for skipping computed pages,
is now handled server side as a function that can be called.

Also removed links to imputed pages from the module finished page. The links were not working
so it did not make sense to display them as links.

Modification to calculate next question needs to be tested more in 8.6.

The following PROBLEM note was noticed in 0.9.0, but may or may not exist in 0.8.6. In 0.9.0,
navigation to next question is based on a linear algorithm to allow users to linearly move
through questions starting at any point in the questionnaire. The PROBLEM note is included in
this commit note for completeness.

PROBLEM: Since the current new routing skips pages with imputed results, it becomes impossible
to navigate through completed questions. If you jump from the finished page to an imputed question
you come back to the finish page. If you jump from the finished page to an answered question in
order to change the answer, you can change the answer, but you do not proceed to the next already
answered question linearly. Instead, the application logic tries to send you to the next answerable
question, which could take you back to the finished page.

RE-ESTABLISHING 0.8.6 ON MACOS with PYTHON 3.8 NOTES
Difficulties were encountered re-establishing an environemnt for development of 0.8.6 on MacOS with
Python 3.8 for this commit.

Basic strategy is to comment out packages having problems in `requirements.txt`, install
as much as possible with `pip install -r requirements.txt`. Install additional packages
as errors are reported for non-existing modules/packages.

Create a virtual environment using Python3 (3.8) and activate.

```
python3 -m venv /path/to/venv860
source /path/to/venv860/bin/activate
```

numpy was having difficulty installing, so comment out numpy lines in `requirements.txt`.

Install requirements.txt file and various other modules.
This avoids having to get all the way through `requirements.txt`.

```
pip install -r requirements.txt 

pip install rtyaml
pip install fs
pip install jinja2
pip install whitenoise
pip install xxhash
pip install html5lib
pip install pillow
pip install python-dateutil
```

Configure GovReady database...

```
python manage.py migrate
python manage.py load_modules
python manage.py first_run

./fetch-vendor-resources.sh

python manage.py runserver 9000
python manage.py runserver 9000

Notes for whitenoise module
# django.core.exceptions.ImproperlyConfigured: WSGI application 'siteapp.wsgi.application' could not be loaded; Error importing module.
# ^C(venv860) Gregs-MacBook-Pro:govready-q-8.6 greg$ pip install whitenoise
# see: https://stackoverflow.com/questions/47800726/django-improperlyconfigured-wsgi-application-myproject-wsgi-application-could


## v0.8.6.4 (October 9, 2019)

* Added security advisory banner to `docs/source/index.md` to upgrade to v0.9.0 or later as soon as possible.
* Documentation updates
* Minor changes to test mock data

## v0.8.6.3 (October 9, 2019)

Version number for internal tracking purposes.

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
