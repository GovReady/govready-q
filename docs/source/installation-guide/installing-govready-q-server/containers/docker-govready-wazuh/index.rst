.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_wazuh_docker:

GovReady-Q and Wazuh via Docker Compose
=======================================

This guide describes how to install GovReady-Q and Wazuh endpoint assessment platform
together using Docker Compose to launch multiple containers.

The containers that are run are:

govready-q: The GovReady-Q server, that assists teams through the compliance process.
wazuh: It runs the Wazuh manager, Wazuh API and Filebeat (for integration with Elastic Stack)
wazuh-kibana: Provides a web user interface to browse through alerts data. It includes Wazuh plugin for Kibana, that allows you to visualize agents configuration and status.
wazuh-nginx: Proxies the Kibana container, adding HTTPS (via self-signed SSL certificate) and Basic authentication.
wazuh-elasticsearch: An Elasticsearch container (working as a single-node cluster) using Elastic Stack Docker images. Be aware to increase the vm.max_map_count setting, as it's detailed in the Wazuh documentation.

Use [Docker Compose](https://docs.docker.com/compose/) to manage the multi-container app.

Docker Compose commands are similar to, but different from, regular Docker commands.  Read the Docker Compose docs for more details.


Installing Docker
-----------------

.. rubric:: Installing with Docker

Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

Installing GovReady-Q server
----------------------------

.. rubric:: Start

.. code-block:: bash

    # To start docker containers in detached mode
    docker-compose up -d

    # Create admin account and organization data
    docker container exec -it govready-q first_run

    # Stop, start container (when needed)
    docker container stop govready-q
    docker container start govready-q

    # View logs - useful if site does not appear
    docker container logs govready-q

    # To stop and remove the containers (and delete user data entered into Q if there no persistent database exists)
    docker-compose down

Visit your GovReady-Q site in your web browser at:

    http://localhost:8000/

Notes and Common Issues
~~~~~~~~~~~~~~~~~~~~~~~

Multiple containers will be created, one for each "service" (as they're called in Docker Compose).

You can check the status of the containers:

```bash
docker-compose ps
```

For additional information on wazuh containers, including configuration information, see: [https://github.com/wazuh/wazuh-docker](https://github.com/wazuh/wazuh-docker)

