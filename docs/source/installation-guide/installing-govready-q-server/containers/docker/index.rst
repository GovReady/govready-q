.. Copyright (C) 2020 GovReady PBC

<<<<<<< HEAD
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
=======
.. _govready-q_server_docker:

Installing GovReady-Q server using Docker
=========================================

GovReady publishes an official GovReady-Q server container based on Unix Ubuntu.

+------------+---------------------------------------------------------+
| Container  | Where                                                   |
+============+=========================================================+
| Current    | https://hub.docker.com/r/govready/govready-q/           |
| Release on |                                                         |
| Docker     |                                                         |
+------------+---------------------------------------------------------+
| Release    | `http                                                   |
| 0.9.0.dev  | s://hub.docker.com/r/govready/govready-0.9.0.dev/ <http |
| on Docker  | s://hub.docker.com/r/govready/govready-q-0.9.0.dev/>`__ |
+------------+---------------------------------------------------------+
| Nightly    | https://hub.docker.com/r/govready/govready-q-nightly/   |
| Build on   |                                                         |
| Docker     |                                                         |
+------------+---------------------------------------------------------+

Choose the Docker install guide that best fits your needs.

+-------------------------------+---------------------------------------------------------------+
| Install                       | Guide                                                         |
+===============================+===============================================================+
| Docker (Unix) Local           | :ref:`Docker Local <govready-q_server_docker_local>`          |
+-------------------------------+---------------------------------------------------------------+
| Docker (Unix) Cloud           | :ref:`Docker Cloud <govready-q_server_docker_cloud>`          |
+-------------------------------+---------------------------------------------------------------+
| Docker (Unix) Advanced Config | :ref:`Advanced config <advanced_container_configuration>`     |
+-------------------------------+---------------------------------------------------------------+
| Docker GovReady+Wazuh (Unix)  | :ref:`Docker GovReady+Wazuh <govready-q_server_wazuh_docker>` |
+-------------------------------+---------------------------------------------------------------+


.. topic:: Contents

    .. toctree::
        :maxdepth: 1

        local
        cloud
        advanced-container-config-examples
        advanced-container-config
>>>>>>> master
