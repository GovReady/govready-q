.. raw:: html

   <style>

   table, tr, td {
       text-align: center;
       background-color: white;
   }

   </style>

Version 0.9.x
=============

What’s New in 0.9.x
-------------------

Release 0.9.x (coming Autumn 2019) is a minor release improving the user
experience and performance.

-  Faster loading and launching of Assessments/questionnaires
-  Simplified install with no subdomains to worry about
-  Replaces subdomain multi-tenancy with simplified “Portfolios” model
-  Improved authoring screens
-  Helpful new start page
-  Adds and updates portfolio level permissions

Release 0.9.x removes multi-tenancy and serves all pages from the same
domain. In the earlier multi-tenancy versions, requests to GovReady-Q
came in on subdomains: the subdomain determined which organization to
associate with the request, and individuals had to re-login across
subdomains. Little value was being realized by actual users for the
subdomain-based multi-tenancy. Removing subdomain-based multi-tenancy
reduces technical debt simplifies deployment.

This release’s compliance apps catalog now reads from the database
rather than constantly rescanning remote repositories and the file
system. The app catalog cache is removed since the page loads much
faster. Release 0.9.x begins to replace the “compliance app” terminology
with the plain language “projects” and “assessment” terminology in end
user pages.

This release also introduces a “Portfolios” feature to organize and
manage related projects.

For a complete list of changes see the `0.9.x.dev branch
CHANGELOG <https://github.com/GovReady/govready-q/blob/0.9.x.dev/CHANGELOG.md>`__.

Release 0.9.x progress can be found on the ``0.9.x.dev`` and
``0.9.x.rc-xxx`` branches.

Screenshots
-----------

.. \|086_sign_in\| image:: assets/086_sign_in.png :width: 480px :alt:
version 0.8.6 sign in page

.. \|090_sign_in\| image:: assets/090_sign_in.png :width: 480px :alt:
version 0.9.x sign in page

.. \|086_projects\| image:: assets/086_projects.png :width: 480px :alt:
version 0.8.6 projects page

.. \|090_projects\| image:: assets/090_projects.png :width: 480px :alt:
version 0.9.x projects page

.. \|090_portfolios_1\| image:: assets/090_portfolios_1.png :width:
480px :alt: version 0.8.6 portfolio create page

.. \|090_portfolios_2\| image:: assets/090_portfolios_2.png :width:
480px :alt: version 0.9.x portfolio detail page

.. \|086_modules\| image:: assets/086_modules.png :width: 480px :alt:
version 0.8.6 module page

.. \|090_modules\| image:: assets/090_modules.png :width: 480px :alt:
version 0.9.x module page

.. \|086_question\| image:: assets/086_question.png :width: 480px :alt:
version 0.8.6 question page

.. \|090_question\| image:: assets/090_question.png :width: 480px :alt:
version 0.9.x question page

Sign-in Page
^^^^^^^^^^^^

+-------------------------+--------------------------+
| **0.8.6 (Old Version)** | **0.9.x (New Version)**  |
| +                       | +                        |
+-------------------------+--------------------------+
| \|086_sign_in\| +       | \|090_sign_in\| +        |
+-------------------------+--------------------------+

Projects List Page
^^^^^^^^^^^^^^^^^^

+-------------------------+--------------------------+
| **0.8.6 (Old Version)** | **0.9.x (New Version)**  |
| +                       | +                        |
+-------------------------+--------------------------+
| \|086_projects\| +      | \|090_projects\| +       |
+-------------------------+--------------------------+

Portfolios (New in 0.9.x)
^^^^^^^^^^^^^^^^^^^^^^^^^

+-------------------------+--------------------------+
| **0.8.6 (Old Version)** | **0.9.x (New Version)**  |
| +                       | +                        |
+-------------------------+--------------------------+
| Feature did not exist + | \|090_portfolios_1\| +   |
+-------------------------+--------------------------+
| Feature did not exist + | \|090_portfolios_2\| +   |
+-------------------------+--------------------------+

Module View
^^^^^^^^^^^

+-------------------------+--------------------------+
| **0.8.6 (Old Version)** | **0.9.x (New Version)**  |
| +                       | +                        |
+-------------------------+--------------------------+
| \|086_modules\| +       | \|090_modules\| +        |
+-------------------------+--------------------------+

Question Page
^^^^^^^^^^^^^

+-------------------------+--------------------------+
| **0.8.6 (Old Version)** | **0.9.x (New Version)**  |
| +                       | +                        |
+-------------------------+--------------------------+
| \|086_question\| +      | \|090_question\| +       |
+-------------------------+--------------------------+

Release Date
------------

The target release date for 0.9.x is Autumn 2019.

Upgrading to 0.9.x from 0.8.x
-----------------------------

**Backup your database before upgrading to 0.9.x. Release 0.9.x performs
database changes that makes rolling back difficult.**

See `Migration Guide for GovReady-Q (0.8.6 to
0.9.x) <migration_guide_086_09x.md>`__.

.. _upgrading-to-0.9.x-from-0.8.x-1:

Upgrading to 0.9.x from 0.8.x
-----------------------------

**Backup your database before upgrading to 0.9.x. Release 0.9.x performs
database changes that makes rolling back difficult.**

See `Migration Guide for GovReady-Q (0.8.6 to
0.9.x) <migration_guide_086_09x.html>`__.

Adding and Managing “Compliance Apps” in 0.9.x
----------------------------------------------

Overview
~~~~~~~~

GovReady-Q wll load a small set of example questionnaires as part of the
``python manage.py first_run`` command during installation.

GovReady-Q must be configured by an administrator to load additional
compliance apps (e.g., assessments and questionnaires) from one or more
sources, which can be local directories or remote git repositories. Full
administrative privileges are assigned to original user account created
when executing ``python manage.py first_run`` during installation.

App Sources are configured in the Django admin at the URL ``/admin`` on
your GovReady-Q domain under ``App Sources``:

.. figure:: assets/appsources_list.png
   :alt: App Sources list

   App Sources list

Each App Source points GovReady-Q to a directory or repository of
compliance apps.

.. figure:: assets/appsource_git_https.png
   :alt: Example App Source

   Example App Source

App Source Slug
~~~~~~~~~~~~~~~

The first App Source field is the Slug. The Slug is a short name you
assign to the App Source to distinguish it from other App Sources. The
Slug is used to form URLs in GovReady-Q’s compliance apps catalog, so it
may only contain letters, numbers, dashes, underscores, and other URL
path-safe characters.

App Source Type
~~~~~~~~~~~~~~~

There are four types of App Sources: local directories, remote git
repositories using HTTP which are typically public repositories, remote
git repositories using SSH which typically use SSH deploy keys for
access, and remote GitHub repositories using a GitHub username and
password for access.

Local Directory
^^^^^^^^^^^^^^^

The Local Directory source type directs GovReady-Q to load compliance
apps from a directory on the same machine GovReady-Q is running on.
(When deploying with Docker, that’s on the container filesystem unless a
path has been mounted to a volume or to the host machine.)

In the ``Path`` field, enter the path to a local directory containing
compliance apps. This path is expected to contain a sub-directory for
each compliance app contained in this source. For instance, if you have
this directory layout:

::

   .
   └── home
       └── user
           └── compliance_apps
               ├── myfirstapp
               │   └── app.yaml
               └── mysecondapp
                   └── app.yaml

then your Path would be ``/home/user/compliance_apps``.

The path can be absolute or relative to the path in which GovReady-Q is
installed.

Git Repository over HTTPS
^^^^^^^^^^^^^^^^^^^^^^^^^

The Git Repository over HTTPS source type is for git repositories, such
as on GitHub or GitLab, that can be cloned using an HTTPS URL. These
repositories are typically public, or in an enterprise environment
public within your organization’s network.

Paste the HTTPS git clone URL — such as
https://github.com/GovReady/govready-apps-dev — into the URL field.
Here’s what that looks like:

.. figure:: assets/appsource_git_https.png
   :alt: App Source for a public git repository

   App Source for a public git repository

The other fields can be left blank.

The ``Path`` field optionally specifies a sub-directory within the
repository in which the compliance apps are stored if they are not
stored in the root of the repository. For instance if the repository has
a directory layout similar to:

::

   .
   └── github.com/organization/repository
       └── apps
           ├── myfirstapp
           │   └── app.yaml
           └── mysecondapp
               └── app.yaml

then set the ``Path`` field to ``apps``.

If the compliance apps are not in the repository’s default branch
(i.e. something other than the typical ``master`` default branch), then
set the ``Branch`` field to the name of the branch to read the
compliance apps from.

You can use HTTPS to access private repositories by placing your
username and password or `personal access
token <https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/>`__
into the URL, such as:

::

   https://username:password@github.com/GovReady/govready-apps-dev

Since this requires user credentials, it should be avoided for
production deployments in favor of using Git Repository over SSH (see
below).

Git Repository over SSH
^^^^^^^^^^^^^^^^^^^^^^^

If your git repository is private and accessible using an SSH URL (which
typically looks like git@github.com:organization/repository.git) and an
SSH public/private keypair, such as with GitHub or GitLab deploy keys,
then use the Git Repository over SSH source type.

Create a new SSH key for your GovReady-Q instance to be used as a deploy
key:

::

   ssh-keygen -q -t rsa -b 2048 -N "" -C "_your-repo-name_-deployment-key" -f ./repo_deploy_key

Your GovReady-Q instance will hold the private key half of the newly
generated keypair, and your source code control system will hold the
public key.

Back in the Django admin, set the Source Type to Git Repository over
SSH. Paste the git clone SSH URL into the URL field. Then open the newly
generated file ``repo_deploy_key`` and paste its contents into the SSH
Key field. Here’s what that looks like:

.. figure:: assets/appsource_git_ssh.png
   :alt: App Source for a private git repository

   App Source for a private git repository

The other fields can be left blank. ``Path`` and ``Branch`` can be set
the same as with the Git Repository over HTTPS source type (see above).

Copy the public key in the newly generated file ``repo_deploy_key.pub``
into the deploy keys section of your source code repository. Here is
what that looks like on GitHub:

.. figure:: assets/github_deploy_key_add.png
   :alt: Adding a deploy key to GitHub

   Adding a deploy key to GitHub

Make the key read only by leaving “Allow write access” field unchecked
and click ``Add the key`` to save the key.

GitHub Repository using the GitHub API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This source type can be used to access private GitHub repositories using
a GitHub username and password or a username and `personal access
token <https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/>`__.

Set the ``Repository`` field to the organization name and repository
name, separated by a slash, as in the repository’s URL following
``github.com/``. In ``Other Parameters``, paste a small YAML-formatted
document holding a GitHub username and password or username and personal
access token, formatted as follows:

::

   auth:
     user: 'myusername'
     pw: 'mypassword'

The other fields can be left blank. ``Branch`` can be set the same as
with the Git Repository over HTTPS source type (see above).

Since this source type requires user credentials, it should be avoided
for production deployments in favor of using Git Repository over SSH.

Compliance Apps
~~~~~~~~~~~~~~~

Compliance Apps are the actual assessments and questionnaires, the “data
packs”, that drive GovReady-Q.

The AppSource admin now lists all of the apps provided by the source and
has links to import new app versions into the database and to see the
app versions already in the database by version number. When the App
Source is defined, additional options appear on the database App Source
admin page to selectively add individual projects and assessments from
the App Source repository to the be published on GovReady-Q. Any time
the individual admin page for an App Source is viewed, the App Source is
rescanned and new versions of the apps are displayed to be selectively
added to be available to users on GovReady-Q.

.. figure:: assets/appsource_apps.png
   :alt: screenshot of App Sources list of apps

   screenshot of App Sources list of apps

When starting a compliance app (i.e. creating a new project), we no
longer have to import the app from the remote repository — instead, we
create a new Project and set its root_task to point to a Module in an
AppVersion already in the database.

App loading is refactored in a few places. The routines for getting app
catalog information from the remote app data are removed since now we
only need it for apps already stored in the database.

The AppSource admin’s approved app lists form is removed since adding
apps into the database is now an administrative function and the
database column for it is dropped.

AppVersion now has a boolean field for whether the instance should be
included in the compliance apps catalog for users to start new projects
with that app.
