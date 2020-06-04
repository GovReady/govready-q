.. Copyright (C) 2020 GovReady PBC

.. _logs:

Logs
====

.. meta::
  :description: Description of GovReady-Q Application Logs.

GovReady-Q logging depends upon the configuration of your system.

* GovReady-Q application logs
* Default Django logs
* Gunicorn (or other WSGI) logs
* NGINX (or other reverse proxy) logs

GovReady-Q Application Logs
---------------------------

As of version 0.9.1.21, GovReady-Q Application logs in a hyprid format with the datetime,
source and level information space delimited and the log message in a JSON object format.
The end goal is to use JSON object format as the default format for the entire log messsage.
The following events are currently logged in this hybrid format.

**"update_permissions portfolio assign_owner_permissions"**

Assign portfolio owner permissions.

.. code:: text

    (pending example)

**"update_permissions portfolio remove_owner_permissions"**

Remove portfolio owner permissions.

.. code:: text

    (pending example)

**"portfolio_list"**

View list of portfolios.

.. code:: text

    2020-06-03 23:53:19,274 siteapp.views level INFO {"user": {"id": 7, "username": "me"}, "event": "portfolio_list"}

**"new_portfolio"**

Create new portfolio.

.. code:: text

    2020-06-03 23:53:20,647 siteapp.views level INFO {"object": {"object": "portfolio", "id": 5, "title": "Security Projects"}, "user": {"id": 7, "username": "me"}, "event": "new_portfolio"}

**"new_portfolio assign_owner_permissions"**

Assign portfolio owner permissions of newly created portfolio to creator.

.. code:: text

    2020-06-03 23:53:20,663 siteapp.views level INFO {"object": {"object": "portfolio", "id": 5, "title": "Security Projects"}, "receiving_user": {"id": 7, "username": "me"}, "user": {"id": 7, "username": "me"}, "event": "new_portfolio assign_owner_permissions"}


**"send_invitation portfolio assign_edit_permissions"**

Assign portfolio edit permissions to a user.

.. code:: text

    2020-06-03 23:53:34,435 siteapp.views level INFO {"object": {"object": "portfolio", "id": 13, "title": "me"}, "receiving_user": {"id": 21, "username": "me2"}, "user": {"id": 20, "username": "me"}, "event": "send_invitation portfolio assign_edit_permissions"}

**"send_invitation project assign_edit_permissions"**

Assign edit permissions to a project and send invitation.

.. code:: text

    (pending example)

**"cancel_invitation"**

Cancel invitation to a project.

.. code:: text

    (pending example)


**"accept_invitation"**

Accept invitation to a project.

.. code:: text

    (pending example)

**"sso_logout"**

Single Sign On logout.

.. code:: text

    (pending example)


**"project_list"**

View list of projects.

.. code:: text

    2020-06-03 23:53:25,902 siteapp.views level INFO {"user": {"id": 14, "username": "portfolio_user"}, "event": "project_list"}

**"start_app"**

Start a questionnaire/compliance app.

.. code:: text

    2020-06-03 23:53:49,721 siteapp.views level INFO {"object": {"task": "project", "id": 23, "title": "My Project Name"}, "user": {"id": 28, "username": "me"}, "event": "start_app"}

**"new_project"**

Create a new project (e.g., questionnaire/compliance app that is a project).

.. code:: text

    2020-06-03 23:53:49,721 siteapp.views level INFO {"object": {"object": "project", "id": 16, "title": "My Project Name"}, "user": {"id": 28, "username": "me"}, "event": "new_project"}

**"new_element new_system"**

Create a new element (e.g., system component) that represents a new system.

.. code:: text

    2020-06-03 23:53:49,722 siteapp.views level INFO {"object": {"object": "element", "id": 3, "name": "My Project Name"}, "user": {"id": 28, "username": "me"}, "event": "new_element new_system"}

    2020-06-03 23:54:07,816 siteapp.views level INFO {"object": {"object": "invitation", "id": 3, "to_email": "user2@example.com"}, "user": {"id": 29, "username": "me2"}, "event": "accept_invitation"}


