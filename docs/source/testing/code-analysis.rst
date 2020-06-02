Code scanning and analysis
==========================

GovReady-Q is a Python web application written on top of the Django framework and uses a variety of industry standard Javascript libraries. See [Software Requirements](requirements.html#software-requirements) for high level view and the ``requirement*.txt`` files for detailed view.

GovReady-Q's Python application code is found in the ``*.py`` files in the following directories and their subdirectories:

* discussion/
* guidedmodules/
* siteapp/

The small ``manage.py`` script in the root directory is part of the Django framework. We use bash utilities scripts (``*.sh``) to automate installation and maintenance tasks of the code base. Python scripts in ``.circleci`` directory are used within our Continuous Implementation pipeline.

Simple Static Code Analysis
---------------------------

To run a static code analysis with our typical settings:

.. code-block:: bash

    bandit -s B101,B110,B603 -r discussion/ guidedmodules/ siteapp/

We use ``-s`` on the command-line and ``nosec`` in limited places in the source code to disable some checks that are determined after review to be false positives.

Detailed Static and Dynamic Code Analysis
-----------------------------------------

We periodically scan GovReady-Q's code base with more traditional/powerful tools and remediate critical and high vulnerabilities.

To scan GovReady-Q's codebase, you will need to configure your tools to scan Python code. You are looking for the ``*.py`` files across the code base.

To scan or do other penetration tests on the code base, we recommend [deploying GovReady-Q with Docker](deploy_docker.html).

