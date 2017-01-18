User Permissions in Q
=====================

This document describes the user permissions model in Q.

What Q tracks
-------------
GovReady Q tracks the following major entities

* Users - individuals with logins to an installed instance of Q
* Organizations - entities, e.g., companies, around with data in Q is segmented
* Systems/Projects - IT systems or IT projects (we use the terms interchangeably)
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

An unauthorized user is always redirected to a login page. The login page does not reveal any Organization data (not even the Organization's display name). If a DNS wildcard enables resolution of all possible Organization subdomains, an unauthorized user cannot tell whether or not an Organization actually exists on the Q deployment.

(Note that *membership* in an Organization is different from *membership* in a Project.)

### Membership in the Organization Project

Each Organization has a single "organization project" which stores additional metadata about the Organization, akin to a User's profile. This metadata can be seen by all members of the Organization because the values, e.g. an organization avatar, may be rendered on Organization pages that any such User may see. Members of the organization project may additionally edit the metadata (see Project membership below).

Projects
--------

A Project is a collection of Tasks being edited by one or more Users. Every Project belongs to exactly one Organization.

### Membership

Projects have zero or more Users who are *members* and zero or more Users who are *administrators*.

Any access to a Project requires *read* access, which is granted if any of the following are true:

* They are a _member_ of the Project.
* They are the editor of a Task within the Project (i.e. guest-style *membership* if they are not otherwise authorized).
* They are a guest participant in a Discussion within the Project.

(This is a subset of the requirements for membership in an Organization, therefore *read* access to a Project guarantees membership in the Organization it belongs to.)

However the Tasks (the questions and answers) within a Project are further restricted (see Tasks below).

Project _members_ can start Tasks listed on the Project page (they become the Task's editor), can send invitations to have another User start a Task (the invited user becomes that Task's editor), and can invite guests to discussions.

Only _administrators_ can send invitations to add new project members, import and export Project data, and delete Projects.

### New Projects

Any member of an Organization can create a new Project within that Organization and becomes the Project's first administrator.

When a User creates a new Project, they are offered project-type Modules that are either

* _not_ marked with `access: private` (see [Schema.md](Schema.md))
* listed in the Organization's `allowed_modules` database field

Tasks
-----

A Task is a set of questions and answers. Each Task belongs to exactly one Project. A Task has an editor, which is the User who has primary responsibility for completing the Task.

A User has *read* access to a Task if any of the following are true:

* They are the editor of the Task.
* They are a _member_ of the Project that the Task belongs to.

A User with *read* access can see the Task on the page for the Project that it belongs to and can see all of its questions, answers, and outputs and can start a Discussion on questions.

A user can also see a particular question within a Task (and its answers and some Task metadata, but not other questions or Task outputs) if they are a guest in a Discussion on that question.

A User has *write* access to a Task if any of the following are true:

* They are the editor of the Task.
* They are an administrator of the Project that the Task belongs to.

A User with *write* access to a Task can answer questions within the Task (which sometimes involves starting new Tasks which they become the editor of), invite other users to become the Task's new editor, and delete/undelete the Task (although there is no UI for that currently).

### Encrypted Answers

We currenly only have one form of encrypted answer, which we call ephemeral encryption. This method of encryption stores a decryption key in a User's browser cookie. Therefore only the User has access to the answer, from the same browser where the question was answered, so long as the cookie is unexpired.
