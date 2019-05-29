# Installing GovReady-Q

.. container:: content-tabs

    .. tab-container:: docker
        :title: Docker

        .. rubric:: Installing with Docker

        Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

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

    .. tab-container:: macos
        :title: macOS

        .. rubric:: Installing on macOS
        
        GovReady-Q calls requires Python 3.6 or higher to run and several Linux packages to provide full functionality.

        .. code-block:: bash

            # install dependencies using brew
            brew install python3
            # other packages: unzip, graphviz, pandoc,
            # xorg-x11-server-Xvfb wkhtmltopdf \

            # optional install gcc to build the uWSGI Python package.
            # Needed on macOS?

            # optional insall of postgress and/or mysql
            # brew install instructions

        .. rubric:: Installing GovReady-Q
        
        Clone GovReady-Q source code and install.

        .. code-block:: bash

            # clone GovReady-Q
            git clone https://github.com/govready/govready-q
            cd govready-q

            # install Python 3 packages
            pip3 install --user -r requirements.txt

            # install Bootstrap and other vendor resources locally
            ./fetch-vendor-resources.sh

        Run the final setup commands to initialize a local Sqlite3 database in `local/db.sqlite` to make sure everything is OK so far:

        .. code-block:: bash

            # run database migrations (sqlite lite database used by default)
            python3 manage.py migrate

            # load a few critical modules
            python3 manage.py load_modules

            # create superuser with initial account
            python3 manage.py first_run

        .. rubric:: Start GovReady-Q

        .. code-block:: bash

            # run the server
            python3 manage.py migrate

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

    .. tab-container:: rhel7
        :title: RHEL/CentOS 7

        .. rubric:: Installing on RHEL/CentOS 7
        
        *Instructions  applicable RHEL 7, CentOS 7 and Amazon Linux 2.*

        GovReady-Q calls requires Python 3.6 or higher to run and several Linux packages to provide full functionality.

        .. code-block:: bash

            # if necessary, enable EPEL and IUS repositories
            rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm https://rhel7.iuscommunity.org/ius-release.rpm

            # install dependencies
            sudo yum install \
            unzip python36-pip python36-devel \
            graphviz \
            pandoc xorg-x11-server-Xvfb wkhtmltopdf \

            # optional install gcc to build the uWSGI Python package.
            sudo yum install gcc

            # optional insall of postgress and/or mysql
            sudo yum install postgresql mysql-devel

        GovReady-Q calls out to `git` to fetch apps from git repositories, but that requires git version 2 or later because of the use of the GIT_SSH_COMMAND environment variable. RHEL stock git is version 1. Switch it to version 2+ by using the IUS package:


        .. code-block:: bash

            # if necessary, remove any git currently installed
            yum remove git
            # install git2u
            yum install git2u

        .. rubric:: Installing GovReady-Q
        
        Clone GovReady-Q source code and install.

        .. code-block:: bash

            # clone GovReady-Q
            git clone https://github.com/govready/govready-q
            cd govready-q

            # install Python 3 packages
            pip3 install --user -r requirements.txt

            # install Bootstrap and other vendor resources locally
            ./fetch-vendor-resources.sh

        Run the final setup commands to initialize a local Sqlite3 database in `local/db.sqlite` to make sure everything is OK so far:

        .. code-block:: bash

            # run database migrations (sqlite lite database used by default)
            python3 manage.py migrate

            # load a few critical modules
            python3 manage.py load_modules

            # create superuser with initial account
            python3 manage.py first_run

        .. rubric:: Start GovReady-Q

        .. code-block:: bash

            # run the server
            python3 manage.py migrate

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

    .. tab-container:: ubuntu
        :title: Ubuntu 16.04

        .. rubric:: Installing on Ubuntu
        
        Instructions provide basic guidance on setting up GovReady-Q on an Ubuntu 16.04 server with Nginx. These commands should be run from the root directory of the GovReady-Q code repository.

        GovReady-Q calls requires Python 3.6 or higher to run and several Linux packages to provide full functionality.

        .. code-block:: bash

            # upgrade apt-get
            apt-get update && apt-get upgrade -y

            # install dependencies
            apt-get install -y \
              unzip \
              python3 python-virtualenvpython3-pip \
              python3-yaml \
              nginx uwsgi-plugin-python3supervisor \
              memcached \
              graphviz

            # optional install gcc to build the uWSGI Python package.
            sudo yum install gcc

            # optional insall of postgress and/or mysql
            apt-get install -y postgresql mysql-devel

        .. rubric:: Installing GovReady-Q
        
        Clone GovReady-Q source code and install.

        .. code-block:: bash

            # clone GovReady-Q
            git clone https://github.com/govready/govready-q
            cd govready-q

            # install Python 3 packages
            pip3 install --user -r requirements.txt

            # install Bootstrap and other vendor resources locally
            ./fetch-vendor-resources.sh

        Run the final setup commands to initialize a local Sqlite3 database in `local/db.sqlite` to make sure everything is OK so far:

        .. code-block:: bash

            # run database migrations (sqlite lite database used by default)
            python3 manage.py migrate

            # load a few critical modules
            python3 manage.py load_modules

            # create superuser with initial account
            python3 manage.py first_run

        .. rubric:: Start GovReady-Q

        .. code-block:: bash

            # run the server
            python3 manage.py migrate

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

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


Additional deployment details and configuration options are documented for each platform.

.. toctree::
   :maxdepth: 1

   deploy_docker.md
   deploy_macos.md
   deploy_rhel7_centos7.md
   deploy_ubuntu.md
   deploy_windows.md
