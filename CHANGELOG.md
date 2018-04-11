GovReady-Q Release Notes
========================

In Development
--------------

Application changes:

* Downloading output documents in 'markdown' format no longer round-trips through pandoc when the template was authored as Markdown.
* Fix caching bug with output documents in multiple formats.
* Small UI improvements.

App authoring changes:

* Templates no longer die but instead show inline error messages when an undefined context variable is accessed.

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

v0.8.0-rc12/v0.8.0-rc13 (April 6, 2018)
---------------------------------------

This release appears to have been tagged twice.

Application changes:

* Minor UI fixes.

Deployment changes:

* Docker deployments now run the container's CMD process as a non-root user.
* Docker deployments now support running with a read-only root filesystem.

Development changes:

* Improvements to the Docker launch scripts.
* Upgraded some dependencies.

v0.8.0-rc11 (April 4, 2018)
---------------------------

Application changes:

* Add a new settings page for administrative functions including setting up the help squad and reviewers and listing organization administrators.
* Minor UI fixes.

App authoring changes:

* Added an 'examples' field to questions for showing example answers on question pages.
* Added 'display: top' option to output documents to show the document at the top of the task finished page.

Development changes:

* Added some tests.
* Upgraded some dependencies.

v0.7.0-rc9/v0.7.0-rc10 (March 30, 2018)
---------------------------------------

This release was incorrectly named with a "7" instead of an "8" and was released twice.

Application changes:

* On the review page, the reviewed state of questions can now be changed with one click.
* Some performance improvements.
* Some UI improvements.
* Fixed a bug in project import with invalid data.

Development changes:

* Pinned a dependency version that changed upstream.
* Minor changes to tests.
* Upgraded some dependencies.

v0.8.0-rc8 (March 21, 2018)
---------------------------

Application changes:

* Discussion comments are now entered using a plain text editor instead of a rich text editor, and @-mention autocompletes are working again.
* Minor bugs fixed.
* Some performance improvements.

Development changes:

* Documentation improvemnts.
* Upgraded some dependencies.

v0.8.0-rc7 (March 16, 2018)
---------------------------

Deployment changes:

* Docker containers wouldn't start if FIRST_RUN wasn't set.

Development changes:

* Upgraded some dependencies.

v0.8.0-rc6 (March 15, 2018)
---------------------------

Application changes:

* Various UI improvements.

App authoring changes:

* Apps can now be hidden by AppSource repositories using a catalog.yaml file.
* AppSources can now control which apps are shown in the catalog.

Deployment changes:

* Various fixes for Docker, including supporting MySQL databases.

Development changes:

* Upgraded some dependencies.

v0.8.0-rc5 (March 7, 2018)
--------------------------

Application changes:

* Fixed crash related to discussion guests on dangling discussions.

Deployment changes:

* Upgraded to the Django 2.0.3 framework.

v0.8.0-rc4 (March 5, 2018)
--------------------------

Application changes:

* Fix a UI problem introduced in the previous release.

v0.8.0-rc3 (March 5, 2018)
--------------------------

Application changes:

* Project import now has a better UI for its results page.
* Various other UI improvements.

Development changes:

* Add static code analysis testing in CircleCI using bandit.
* Added code coverage artifact to CircleCI builds.
* Upgraded some dependencies.

v0.8.0-rc2 (Feb. 28, 2018)
--------------------------

Deployment changes:

* Docker: Install mysqlclient so MySQL databases are supported.
* The installation of psycopg2 in the Dockerfile is now in requirements.txt so its hashes are checked when downloaded.

Development changes:

* Upgraded some dependencies.

v0.8.0-rc1 (Feb. 28, 2018)
--------------------------

Application changes:

* Fixes related to recent performance improvements.

Development changes:

* Upgraded some dependencies.

v0.8.0-rc0 (Feb. 27, 2018)
--------------------------

Application changes:

* The homepage listing projects and folders has been revamped to lay out compliance projects in lifecycle stage columns.
* Project pages now arrange tasks in columns as well according to the completion status of the task, tasks have progress bars showing completion, and module-set questions with multiple answers are now shown as separate entries.
* Added a button to clear the compliance apps catalog cache to the bottom of the app catalog page that only users with the Django appsource_change permission can see.
* Added various error handling for invalid app content and invalid AppSource configurations.
* Tasks whose titles are automatically set by rendering the instance-name field now revert back to the module title string if the instance-name field refers to a question that has not yet been answered.
* Various cosmetic changes.
* Various speed improvements.

App authoring changes:

* Improved the app authoring tools.
* The ephemeral encryption feature was removed.
* The "required" field on questions was removed.
* The "tab" field on questions was removed.
* The "external-function" question type was removed.
* Updated documentation screenshots.
* Add a new management command for taking screenshots of starting a compliance app and answering its questions to make documentation writing easier.

Administrative changes:

* Improved the AppSource admin page to clarify setting up public and private git repositories.
* AppSources for git repositories now use the repository's default branch instead of "master," since it might not be "master," if a branch is not specified.

Deployment changes:

* Docker image now uses CentOS 7 rather than Debian.
* Docker deployments now have more logging.
* Upgraded to the Django 2.0.2 framework.
* Documentation improvements.

Development changes:

* Upgraded our CircleCI CI pipeline to CircleCI 2.0.
* Added ability to run unit tests within the Docker deployment container.
* Replaced hard-coded test passwords with randomly generated strings.
* Small changes to avoid false positives in static code scanning.

v0.7.0-rc2 (January 8, 2018)
----------------------------

First release.
