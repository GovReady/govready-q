.. Copyright (C) 2020 GovReady PBC

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
        advanced-container-config-example
        advanced-container-config