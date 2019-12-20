GovReady-Q Release Notes
========================

v0.9.0.2.3 (November 8, 2019)
-----------------------------

For Mesosphere deployment, fetch and pre-collect the static files into `static_root`.
Make sure vendor and siteapp/static/vendor files are no longer gitignored.

v0.9.0.2.2 (November 7, 2019)
-----------------------------

For Mesosphere deployment, fetch and pre-collect the static files into `static_root`.

v0.9.0.2.1 (October 18, 2019)
-----------------------------

Modifications to container deployment environmental variables to better support deployments in Mesosphere and other Docker orchestration environments.

**WARNING - CONTAINER ENVIRONMENTAL VARIABLE CHANGES**

The `HOST` and `PORT` container deployment environmental variables renamed to `GR_HOST` and `GR_PORT`. Update your container-based deployment configurations accordingly.

**Developer changes:**

* Change `HOST` and `PORT` container deployment environmental variable names to avoid name collision. Update container-based deployment configurations accordingly.

**Documentation changes:**

* Change `HOST` and `PORT` container deployment environmental variable names to avoid name collision in Mesosphere and other container orchestration tools.

=======

v0.9.0.3 (November 21, 2019)
-------------------------------

**UX changes:**

* Significantly improve performance of rendering questions and module review page (PR #774)
* Fix failure to display list of questions in progress history in certain circumstances

**Developer Change**

* Create migrations for shortening varchar field length to 255 on siteapp.models

**Deployment Change**

* Adding in health paths to examine static files.
