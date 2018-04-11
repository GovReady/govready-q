GovReady-Q Release Notes
========================

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
