.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_sources_ubuntu:

Docker
======

This guide describes how to install the GovReady-Q server using Docker.


Installing Docker
-----------------

.. rubric:: Installing with Docker

Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

Installing GovReady-Q server
----------------------------

.. rubric:: Start

.. code-block:: bash

    # Run the docker container in detached mode
    docker container run --name govready-q --detach -p 8000:8000 govready/govready-q

    # Create admin account and organization data
    docker container exec -it govready-q first_run

    # Stop, start container (when needed)
    docker container stop govready-q
    docker container start govready-q

    # View logs - useful if site does not appear
    docker container logs govready-q

    # To destroy the container and all user data entered into Q
    docker container rm -f govready-q


Visit your GovReady-Q site in your web browser at:

    http://localhost:8000/