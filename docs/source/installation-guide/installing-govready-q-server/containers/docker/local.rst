.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_docker_local:

Docker Local
============

These instruction are for running a basic version of GovReady-Q
locally on your workstation.

This configuration assumes a simple network configuration where you will be
viewing GovReady-Q from the same host that is hosting the docker instance.


1. Installing Docker
--------------------

Make sure you first install Docker (https://docs.docker.com/engine/installation/) and,
if appropriate, grant non-root users access to run Docker containers
(https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user)
(or else use `sudo` when invoking Docker below).


2. Running GovReady-Q server container
--------------------------------------

We recommend you launch GovReady-Q container in the detached mode.

The following commands will launch GovReady-Q using the default SQLITE database.

.. code-block:: bash

    # Run the docker container in detached mode
    docker container run -d --name govready-q -p 8000:8000 govready/govready-q

    # Create GovReady-Q Django Superuser account and organization interactively on the commandline
    docker container exec -it govready-q first_run

    # Alternatively create GovReady-Q Django Superuser account and organization interactively on the commandline
    # docker container exec -it govready-q first_run --non-interative

Visit your GovReady-Q site in your web browser at:

    http://localhost:8000/

Your GovReady-Q site will not load immediately, as GovReady-Q
initializes your database for the first time. Wait for the site to
become available.

The default Govready-Q instance is configured to non-debug mode (Django
``DEBUG=false``), which is the recommended setting for a public website.
The instance can be set to debug mode at runtime.

.. note::
    The command ``docker container exec -it govready-q first_run`` creates the Superuser interactively allowing you to specify username and password.

    The command ``docker container exec -it govready-q first_run --non-interactive`` creates the Superuser automatically for installs where you do
    not have access to interactive access to the commandline. The auto-generated username and password will be generated once to
    to the standout log. When running the Docker containter in the detached (``-d``) mode, you can access the standout log with the command ``docker container logs govready-q``.

.. warning::
    The GovReady-Q default SQLite database created within a Docker container
    exists only for the duration of the container’s lifetime. The database
    will persist between
    ``docker container stop``/``docker container start`` commands, but when
    the container is removed from Docker (i.e. using
    ``docker container rm``) the database will be destroyed.


3. Stopping, starting GovReady-Q server container
-------------------------------------------------

.. code-block:: bash

    # Stop, start container (when needed)
    docker container stop govready-q
    docker container start govready-q


4. Destroying the GovReady-Q server container
---------------------------------------------

.. code-block:: bash

    # Destroy the container and all user data entered into local database
    docker container rm -f govready-q


5. Viewing the GovReady-Q server logs in the container
--------------------------------------------------------

.. code-block:: bash

    # View logs - useful if site does not appear
    docker container logs govready-q


Advanced configuration options
------------------------------

The GovReady-Q server container supports many advanced configuration options
for production deployments.

See the next section `Advanced container configuration <advanced-container-config.html>`__  for further details.


.. topic:: Contents

    .. toctree::
        :maxdepth: 1

        cloud
        advanced-container-config