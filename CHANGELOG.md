GovReady-Q Release Notes
========================

In Development
--------------

Application changes:

* Minor UI improvements.
* Minor bug fixes.

Deployment changes:

* Docker launch failed if `HTTPS` environment variable was not passed in.
* Added a new `branding` environment setting for sites to override templates and provide new assets using a custom Django app.

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
