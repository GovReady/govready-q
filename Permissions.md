User Permissions in Q
=====================

This document describes the user permissions model in Q.

What Q tracks
-------------
GovReady Q tracks the following major entities

* Users - individuals with logins to an installed instance of Q
* Organizations - entities, e.g., companies, around with data in Q is segmented
* Folders - collections of Projects
* Projects - instantiations of Compliance Apps
* Membership - associating individual users with organizations and systems
* Tasks/Modules - coherent grouping of questions and educational content
* Questions/Answers - specific snippet of content within a Task
* Templates - drives automatic generation of artifacts, supporting variable subsitution

Users
-----

### Global user data

A User is authenticated by a unique username and a hashed password.

Each User has one or more email addresses associated with their account and notification email settings.

User accounts --- i.e. the fields above --- are global to a Q deployment. They are _not_ segmented by Organization. For instance, if a User has been created for one Organization, they sign in --- and not sign up --- into other Organizations. Changing a User's password changes it for all Organizations. (Of course, a User will not be _authorized_ to access all Organizations. See the next section on Organizations.)

### Segmented user data

Each User additionally has a unique "organization user profile" associated with each organization to support the same User having different roles at different organizations. (This user profile is an "account project" that holds additional User information including a User's full name, profile photo, etc. In short, each User has a different profile in each Organization.

The profile information can be seen by all other members of the Organization because it is used in the history of question answers, notifications, discussions, and many other places. 

(The User is the only "member" of their account projects (see Project *membership* below), which means they are the only User who can edit the information.)

### System staff

Users marked as `staff` in the Django admin can see Q Analytics.

Organizations
-------------

Each deployment of Q serves one or more Organizations. Each Organization is served off of a unique subdomain.

Organizations are used to segment Projects and the data contained within them to create data isolation both at a logical level and because of the use of subdomains at the HTTP level. (Organizations hosted by the same Q deployment use a single database backend, however.)

All pages on an Organization subdomain require *membership* in the Organization to be accessed. A User has *membership* in an Organization if they are authenticated and any of the following are true:

* They are a _member_ of a Project within the Organization (see Project *membership* below).
* They are the editor of a Task within the Organization (i.e. guest-style *membership* if they are not otherwise authorized).
* They are a guest participant in a Discussion within the Organization.
* They clicked an invitation URL, which gives them access to the invitation landing page only.

An unauthorized user is always redirected to a login page. GovReady-Q can be configured with the `organization-seen-anonymously` setting to not reveal any Organization data (not even the Organization's display name) on the login page, and if that setting is turned on, and if a DNS wildcard enables resolution of all possible Organization subdomains, an unauthorized user cannot tell whether or not an Organization actually exists on the Q deployment.

(Note that *membership* in an Organization is different from *membership* in a Project.)

### Membership in the Organization Project

Each Organization has a single "organization project" which stores additional metadata about the Organization, akin to a User's profile. This metadata can be seen by all members of the Organization because the values, e.g. an organization avatar, may be rendered on Organization pages that any such User may see. Members of the organization project (which is different from members of the organization itself) may additionally edit the metadata (see Project membership below).

Folders
-------

A Folder is a collection of one or more Projects (see below) within the same Organization.

Folder permissions are based in part on Project permissions:

* A user can see that a Project is a part of a Folder if the user has *read* access on the Project.
* A user can add Projects to a Folder or rename a Folder if the user is an _administrator_ of any Project within the Folder *or* is an _administrator_ of the Folder itself. These users may not be able to see all Projects within the folder if they do not have *read* access to those Projects, but they will be told how many Projects they can't see in the Folder.

There is no separate "read" permission on a Folder. A Folder can be seen just when a user has *read* access on a Project within it or is an _administrator_ of the Folder itself.

Projects
--------

Each time an app is started from the Compliance Store, a new Project is created. A Project represents the instantiated app and is comprised of a collection of Tasks. Every Project belongs to exactly one Organization.

### Membership

Projects have zero or more Users who are *members* and zero or more Users who are *administrators*.

### Read Access

Any access to a Project requires *read* access, which is granted if any of the following are true:

* They are a _member_ or _administrator_ of the Project.
* They have *read* access to any Task in the project.
* They are a guest participant in a Discussion within the Project.

(This is a subset of the requirements for membership in an Organization, therefore *read* access to a Project guarantees membership in the Organization it belongs to.)

### Operations

Project _members_ can begin Tasks listed on Project pages, either by adding apps from the Compliance Store or starting Tasks for modules contained in the Project's app. Project _members_ can also invite guests to discussions.

Only _administrators_ can send invitations to add new project members, import and export Project data, and delete Projects.

The Tasks (the questions and answers) within a Project are further restricted (see Tasks below).

### New Projects

Any member of an Organization can create a new Project within that Organization by starting a new Compliance App and becomes the Project's first administrator.

When a User creates a new Project, they are offered Compliance Apps from AppSources whose `Available to all` option is checked and from AppSources that don't have 'Available to all' checked but explicitly list the Organization in its 'Available to orgs' list.

New Projects are added into a new or existing Folder (for existing folders, see Folder permissions above).

Tasks
-----

A Task is a set of questions and answers. Tasks represent the state of a Project --- each Project has a root Task --- as well as the state of all the modules started within the Project.

Each Task belongs to exactly one Project. Each Project has exactly one root Task.

A Task has an editor, which is the User who has primary responsibility for completing the Task.

A User has both *read* and *write* access to a Task if any of the following are true:

* They are the editor of the Task.
* They are a _member_ or _adminstrator_ of the Project that the Task belongs to.

A User with *read* access can see the Task on the page for the Project that it belongs to and can see all of its questions, answers, and outputs and can start a Discussion on questions.

A user can also see a particular question within a Task (and its answers and some Task metadata, but not other questions or Task outputs) if they are a guest in a Discussion on that question.

A User with *write* access to a Task can answer questions within the Task (which sometimes involves starting new Tasks which they become the editor of), invite other users to become the Task's new editor, and delete/undelete the Task (although there is no UI for that currently).

### Encrypted Answers

We currenly only have one form of encrypted answer, which we call ephemeral encryption. This method of encryption stores a decryption key in a User's browser cookie. Therefore only the User has access to the answer, from the same browser where the question was answered, so long as the cookie is unexpired.
