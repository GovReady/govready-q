.. role:: raw-html-m2r(raw)
   :format: html

Migration Guide for GovReady-Q v0.8.6 to v0.9.0
===============================================

Major Changes between v0.8.6 and v0.9.0
---------------------------------------

Changes GovReady-Q users will encounter in v0.9.0:

* Organization subdomains are no longer used - everything is on the main domain.
* Individual Questionnaires/Assessments from an App Source must now be explicitly added to the catalog via the Django admin page. More information can be found in the version 0.9.0 section of the GovReady-Q documentation.
* Assessments are referred to as “Projects” in the UI.
* “Projects” are organized into “Portfolios.” Every Project belongs to exactly one Portfolio.
* Users can be added to Portfolios and be granted different permissions in Portfolios via an improved permission model.

.. list-table::
   :header-rows: 1
   :class: tight-table 

   * - **v0.8.6**
     - **v0.9.0**
     - **What migrating does**
   * - Subdomains.
     - Single domain.
     - Single domain is used as per ``host`` param in ``local/environment.json`` file or Docker config params.
   * - Organizations associated with different subdomains.
     - Single “master” organization.
     - A "Portfolio" is created for each Organization with the same name as the Subdomain. Organizations continue to exist in database, but are not used.
   * - Users are associated with multiple subdomain organizations.
     - All users associated with single instance.
     - Preserves users.
   * - User have different profiles for each subdomain organization.
     - User has single profile.
     - First profile is kept and can be edited by user.
   * - User "is staff" and "is super user" set in Django Admin.
     - User "is staff" and "is super user" set in Django Admin.
     - Roles preserved, see Roles and Permissions in v0.9.0 section.
   * - Started and completed apps.
     - Started and completed apps.
     - All existing apps/questionnaires are preserved. Each questionnaire becomes associated with the "Portfolio" having the same name as the Organization to which the project was previously associated.
   * - User signs in under each subdomain.
     - User signs in once.
     - Subdomain associates are removed.

Complete list of changes: `https://github.com/GovReady/govready-q/blob/0.9.0.dev/CHANGELOG.md <https://www.google.com/url?q=https://github.com/GovReady/govready-q/blob/0.9.0.dev/CHANGELOG.md&sa=D&ust=1567539997944000>`_.

Migration Process
-----------------

General Guidelines
^^^^^^^^^^^^^^^^^^

* Make sure your live data is backed up, and can be found and restored properly, before, during, and after the migration.
* Do test migrations on test servers first, to ensure you understand the process and have worked out any kinks, before working on production servers.
* Check for customizations, and preserve or modify them as needed.

Back Up Your Production Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Ensure that you have a backup of your production data, and that it is safe, and will be available for a successful restore.

Read the Documentation
^^^^^^^^^^^^^^^^^^^^^^

* Familiarize yourself with the migration process before conducting the first test migration.
* Make sure GovReady-Q official documentation is working for you.

Do a Test Migration
^^^^^^^^^^^^^^^^^^^

* Use test data that will model and exercise the same features as your production data.
* Use a clean install of the version you run in production, with test data installed.
* Migrate your customizations to the test platform.
* Perform the upgrade to v0.9.0.release.
* Test to ensure the upgrade performed properly.  Keep notes as you test.
* Repeat until you're comfortable with the process and results.
* Optionally have selected end-users sign into the upgraded test instance to perform their own tests.

Distribute a Migration Plan
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Create a migration plan. Include user impacts, timelines, contingency plans, and technical details (perhaps in a separate technical plan).
* Confirm that your colleagues who are responsible, accountable, consulted, and informed about the migration are satisfied with the plan.
* Distribute the plan to anybody affected.
* When migration starts, communicate to users that migration is starting, and keep a communication line with them open.

Do the Production Migration for Deployments with Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Take your GovReady-Q instance offline.
* Back up the most recent version of the production database.
* Test a restore of most recent version of the database.
* Update code to version 0.9.0.release.
* Run ``pip install -r requirements.txt`` to get new libraries.

  .. raw:: html

     <!-- * [Coming soon: Run the migration checker to compare files for impact to your customized files.]  -->

* Update any template and file customizations in your workstream.
* Run ``python manage.py migrate`` to update your database schema.
* Run ``python manage.py runserver`` to run your updated instance.

Do the Production Migration for Deployments with Docker/Containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Take your GovReady-Q instance offline.
* Back up the most recent version of the production database.
* Test a restore of most recent version of the database.
* Synchronize your container customizations to produce a new version of your container.
* Deploy container running version 0.9.0 **with environment variable ``DB_BACKED_UP_DO_UPGRADE`` set to "True"**. (This special environment variable is required to avoid accidental running of database migrations before database has been backed up.)
* Docker will automatically run migrations as part of deployment.

Migration Finalization and Testing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Test the new instance.
* Back up the newly migrated production database.

Post Migration Clean Up
^^^^^^^^^^^^^^^^^^^^^^^

* Mark all old Notifications ``emailed`` as True. (v0.9.0 notification checks emailed status of notifications and sets emailed to True after email is sent.)
* Review Help Squad, Reviewers, and Administrators. 

  * The migration converts Organizations to Portfolios. 
  * Help Squad, Reviewers, and Organization admins are only preserved on the “main” organization (e.g., first organization created). 
  * The migration does not modify the Help Squad or Reviewers. 
  * Organization Admins are associated with the “main” organization. 

* You should review who has these permissions and adjust accordingly after migrating.
* Release the production instance to users.

Roles and Permissions in v0.9.0
-------------------------------

.. list-table::
   :header-rows: 1
   :class: tight-table 

   * - **Permission/Role Name**
     - **Description**
     - **What Happens During Migration**
   * - Organization > get_who_can_read
     - A user can see an Organization if: they have read permission on any Project within the Organization, they are an editor of a Task within a Project within the Organization (but might not otherwise be a Project member), they are a guest in any Discussion on TaskQuestion in a Task in a Project in the Organization.
     - A Portfolio is created for every organization that exists.
   * - projectmembership
     - See Project > has_read_priv
     - See below.
   * - Project > has_read_priv (Inverse is Project > get_all_participants)
     - Team members + anyone with read privs to a task within this project + anyone who is a guest in discussion within this project.
     - See below.
   * - Project > is_admin
     - Person flagged as project admin in ProjectMembership.
     - Grant project_delete permission on project and portfolio_owner permission for portfolio for which project is a part
   * - Project > is_member Project > editor_of task(s)Project > discussion_guest_in discussion(s)
     - Various permissions in a project.
     - Grant project_view, project_add, project_change, for project of which project is a part; Grant Portfolio_view, portfolio_add, portfolio_change for which project is a part after migration.
   * - task_editor
     - The user that has primary responsibility for completing this Task.
     - Grant project_view, project_add, project_change, for project of which task is a part; Grant Portfolio_view, portfolio_add, portfolio_change for which task is a part after migration.
   * - help_squad
     - Receives all discussion messages
     - Not modified by migration
   * - reviewer
     - Can set review status of answers.
     - Not modified by migration
   * - superuser
     - Django designated superuser.
     - Not modified by migration
   * - Folder permissions
     - A folder object exists but is not used.
     - Not modified by migration
   * - portfolio_owner
     - Permission on portfolio object, can invite others to portfolio and can make others to portfolio owner
     - If user was project_membership and had project_membership admin flag True, user is made portfolio owner.
   * - Portfolio_view, portfolio_add, portfolio_delete, portfolio_change
     - Permissions on Portfolio objects. Currently everyone who has one of these has all of these permissions.
     - Every user gets a portfolio with their name for which user is the portfolio_owner. For every organization, a portfolio is created with the same name and associating the organization projects with the portfolio. Users get access to the projects.
   * - project_view, project_add, project_change, project_delete
     - Permissions on Project objects. Currently everyone who has one of these has all of these permissions.
     - If user has project_membership on project, user gets project_view, project_add, project_change.  If user has project_membership on project and project_membership admin flag True, user also gets project_delete. If user has task object for a project, user gets project_view, project_add, project_change.  If user is a guest of a discussion object for a project, user gets project_view, project_add, project_change.

