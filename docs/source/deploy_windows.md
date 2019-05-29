# Deploying on Windows (with Docker)

## Quickstart

.. container:: content-tabs

    .. tab-container:: windows
        :title: Windows

        .. rubric:: Installing on Windows (with Docker)

        GovReady-Q can only be installed on Windows using Docker.

        Make sure you first [install Docker](https://docs.docker.com/engine/installation/) and, if appropriate, [grant non-root users access to run Docker containers](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

        .. rubric:: Start

        .. code-block:: bash

            # Run the docker container in detached mode
            docker container run --name govready-q --detach -p 8000:8000 govready/govready-q

            # Create admin account and organization data
            docker container exec -it govready-q first_run

            # Stop, start container
            docker container stop govready-q
            docker container start govready-q

            # View logs - useful if site does not appear
            docker container logs govready-q

            # To destroy the container and all user data entered into Q
            docker container rm -f govready-q


        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

## Additional Details

We welcome assistance with installing GovReady-Q natively on Windows.
