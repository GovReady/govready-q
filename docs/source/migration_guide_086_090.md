# Migration Guide for GovReady-Q (0.8.6 to 0.9.0)

## Major Changes Between 0.8.6 and 0.9.0

Changes GovReady Q users will encounter in 0.9.0:

- Organization subdomains are no longer used - everything is on the main domain.
- Individual Questionnaires/Assessments from an App Source must now be explicitly added to the catalog via the Django admin page. More information can be found in the version 0.9.0 section of the Q documentation.
- Assessments are referred to as “Projects” in the UI.
- “Projects” are organized into “Portfolios.” Every Project belongs to exactly one Portfolio.
- Users can be added to Portfolios and be granted different permissions in Portfolios via an improved permission model.

| **v0.8.6**                                                   | **v0.9.0**                                              | **What migrating does**                                      |
| ------------------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------ |
| Subdomains                                                   | Single domain                                           | Single domain is used as per _________.                      |
| Organizations associated with different subdomains           | Single “master” organization.                           | A “Portfolio” is generated for each Organization with the same name as the Subdomain. A single “master” organization is kept. |
| Users are associated with multiple subdomain’ed organizations. | All users associated with “master” organization.        |                                                              |
| User have different profiles for each subdomain organization. | User has single profile.                                | First profile is kept. Can be edited by user.                |
| User “is staff” and “is super user” set in Django Admin      | User “is staff” and “is super user” set in Django Admin | Same.                                                        |
| Started and completed apps                                   | Started and completed apps                              | All existing apps/questionnaires are preserved. Each questionnaire becomes associated with the “Portfolio” having the same name as organization. |
| User must sign in under each subdomain each subdomain organization. | User signs in once.                                     | Subdomain associates are removed. No other changes. GovReady-Q used same credentials for all subdomains. |

Complete list of changes: [https://github.com/GovReady/govready-q/blob/0.9.0.dev/CHANGELOG.md](https://www.google.com/url?q=https://github.com/GovReady/govready-q/blob/0.9.0.dev/CHANGELOG.md&sa=D&ust=1567539997944000).

## Migration Process Summary

### General Guidelines
* Make sure your live data is backed up, and can be found and restored properly, before, during, and after the migration.
* Do test migrations on test servers first, to ensure you understand the process and have worked out any kinks, before working on production servers.
* Check for customizations, and preserve or modify them as needed.

### Back Up Your Production Data
* Ensure that you have a backup of your production data, and that it is safe, and will be available for a successful restore.

### Read The Documentation
* Familiarize yourself with the migration process before conducting the first test migration.
* Make sure GovReady-Q official documentation is working for you.

### Do A Test Migration
* Use test data that will model and exercise the same features as your production data.
* Use a clean install of the version you run in production, with test data installed.
* Migrate your customizations to the test platform.
* Perform the upgrade to 0.9.0.release.
* Test to ensure the upgrade performed properly.  Keep notes as you test.
* Repeat until you're comfortable with the process and results.
* Optionally have selected end-users sign into the upgraded test instance to perform their own tests.

### Distribute A Migration Plan
* Create a migration plan.  Include user impacts, timelines, contingency plans, and technical details (perhaps in a separate technical plan).
* Confirm that your colleagues who are responsible, accountable, consulted, and informed about the migration are satisfied with the plan.
* Distribute the plan to anybody affected.
* When migration starts, communicate to users that migration is starting, and keep a communication line with them open.

### Do The Production Migration
* Take Q offline.
* Back up the most recent version of the production database.
* Test a restore of most recent version of the database.
* Update code to version 0.9.0.release.
* [run the migration checker to compare files] 
* Update any template and file customizations in your workstream.
* Update the DB schema.
* Run the new instance.

### Migration Finalization and Testing
* Test the new instance.
* Back up the newly migrated production database.
* Release the production instance to users.

### Post Migration Clean Up
* Mark all old Notifications `emailed` as True. (0.9.0 notification checks emailed status of notifications and sets emailed to True after email is sent.)
* Review Help Squad, Reviewers, and Administrators. 
    - The migration converts Organizations to Portfolios. 
    - Help Squad, Reviewers, and Organization admins are only preserved on the “main” organization (e.g., first organization created). 
    - The migration does not modify the Help Squad or Reviewers. 
    - Organization Admins are associated with the “main” organization. 
* You should review who has these permissions and adjust accordingly after migrating.
* [see comments]


## Detailed Migration Process

### Before migrating
1. Ensure that permissions are set up to your specifications, because this is easier in 0.8.6 than in 0.9.0.
    a. Change from 0.8.6: project admin functionality is now linked more strongly to the Django admin role. So, you may need to mark additional users as “Staff” in the Django admin panel (at <BASE_URL/admin>).
2. Stop the Q web process (i.e., stop the `python3 manage.py runserver` process). This will ensure that nobody accesses Q while it’s in an unsafe or intermediate state.
3. Backup your database, in case you need to restore to the previous version. (there are no rollback scripts provided, so restoring from a backup will be the easiest way to achieve a rollback)
4. Note and address any customizations you have such as template overrides or settings.py overrides. Templates and python files have changed in 0.9.x
5. Run the Protected File Notification utility to identify any source code files you have customized that will be impacted by the upgrade. It is your responsibility to track source code files your organization has customized with changes that need to be protected (e.g., maintained or adjusted) for customized functionality.

### Performing the migration

#### Using a git repository

If you are running Q from its git repository, the migration steps are:

1. Switch to the 0.9.0.rc-002 code, using `git checkout 0.9.0.rc-002`
2. Update the DB schema, using `python3 manage.py migrate`

#### Using Docker

* [todo - stuff goes here]

### After the migration
1. Re-start the web process (`python3 manage.py runserver`)
2. Spot-check the site to verify that your data has been migrated successfully. If something is amiss, contact the GovReady Q development team for assistance at info@govready.com.
3. In 0.9.0, Apps contained in an App Source must be explicitly added to a catalog of available Apps. You will most likely want to do this now, using the Django admin page (at <BASE_URL/admin>).
4. Organization-specific subdomains no longer exist, and can be safely decommissioned. e.g., you may wish to set up redirects from legacy subdomains to the main domain.
5. Inform your users that the new version is up and running.


## Roles And Permissions in 0.9.0

| **Permission/Role Name**                                     | **Description**                                              | **What Happens During Migration**                            |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Organization > get_who_can_read                              | A user can see an Organization if: * they have read permission on any Project within the Organization * they are an editor of a Task within a Project within the Organization (but might not otherwise be a Project member) * they are a guest in any Discussion on TaskQuestion in a Task in a Project in the Organization | A Portfolio is created for every organization that exists.   |
| projectmembership                                            | See Project > has_read_priv                                  | See below                                                    |
| Project > has_read_priv (Inverse is Project > get_all_participants) | # Who can see this project? Team members + anyone with read privs to a task within        # this project + anyone that's a guest in dicussion within this project.        # See get_all_participants for the inverse of this function. | See below                                                    |
| Project > is_admin                                           |                                                              | Grant project_delete permission on project and portfolio_owner permission for portfolio for which project is a part |
| Project > is_member Project > editor_of task(s)Project > discussion_guest_in discussion(s) |                                                              | Grant project_view, project_add, project_change, for project of which project is a part; Grant Portfolio_view, porfolio_add, portfolio_change for which project is a part after migration. |
| task_editor                                                  | The user that has primary responsibility for completing this Task. | Grant project_view, project_add, project_change, for project of which task is a part; Grant Portfolio_view, porfolio_add, portfolio_change for which task is a part after migration. |
| help_squad                                                   | Receives all discussion messages                             | Not modified by migration                                    |
| reviewer                                                     | Can set review status of answers.                            | Not modified by migration                                    |
| superuser                                                    |                                                              | Not modified by migration                                    |
| Folder permissions                                           | A folder object exists but is not used.                      | Not modified by migration                                    |
| portfolio_owner                                              | Permission on portfolio object, can invite others to portfolio and can make others to portfolio owner | If user was project_membership and had project_membership admin flag True, user is made portfolio owner. |
| Portfolio_view, porfolio_add, portfolio_delete, portfolio_change | Permissions on portfolio objects. Currently everyone who has one of these has all of these permissions. | Every user gets a portfolio with their name for which user is the portfolio_owner. For every organization, a portfolio is created with the same name and associating the organization projects with the portfolio. Users get access to the projects, |
| project_view, project_add, project_change, project_delete    |                                                              | If user has project_membership on project user gets project_view, project_add, project_change.  If user has project_membership on project and project_membership admin flag True, user also gest project_delete. If user has task object for a project, user gets project_view, project_add, project_change.  If user user is a guest of a discussion object for a project, user gets project_view, project_add, project_change. |



