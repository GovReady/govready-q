GovReady-Q Release Notes
========================

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
