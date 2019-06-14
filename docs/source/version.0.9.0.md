# Version 0.9.0

Release 0.9.0 (coming July 2019) is a minor release improving
the user experience and performance.

* Faster loading and launching of Asssessments/questionnaires
* Simplified install with no subdomains to worry about
* Replaces subdomain multi-tenancy with simplified "Groups" model
* Improved authoring screens
* Helpful new start page

Release 0.9.0 removes multi-tenancy and serves all pages from the on the same domain. In earlier versions, requests to GovReady-Q came in on subdomains and the subdomain determined which Organization in the database the request would be associated with and individuals had to re-login across subdomains. Multitenancy increased install complexity and we were not seeing use of the multitenancy feature. Deployment is now simpler.

This release's compliance apps catalog now reads from the database rather than going to remote repositories The app catalog cache is removed since the page loads much faster. Release 0.9.0 begins to replace the "compliance app" terminology with the plain language "projects" and "assessment" terminology in the end user pages.

This release also introduces a "Group" feature to organize and manage related projects.

For a complete list of changes see the [0.9.0.rc branch CHANGELOG](https://github.com/GovReady/govready-q/blob/0.9.0.rc/CHANGELOG.md).

Release 0.9.0 progress can be found on the `0.9.0.rc-xxx` branches. For the convience of this documentation and building Docker containers, the branch `0.9.0.rc` has also been created.

## Release Date

The target release date 0.9.0 is July 2019.

## Upgrading to 0.9.0 from 0.8.x

**Backup your database before upgrading to 0.9.0. Release 0.9.0 performs database changes that makes rolling back difficult.**

If you are installing from source code:
1. Pull and use the [0.9.0-rc branch](https://github.com/GovReady/govready-q/tree/0.9.0.rc).
2. Tell Django to run the database migrations (e.g., `python manage.py migrate`).
3. We recommend updating to your `local/environment.json` file to address release 0.9.0's removal of the need to manage subdomain-based multi-tenancy.

If you are installing using Docker:
1. Make sure you pull the [0.9.0-rc container](https://cloud.docker.com/u/govready/repository/docker/govready/govready-q-0.9.0.rc).
2. If you are using environmental parameters to connect the Docker deployment to a persistent database, GovReady-Q will automatically run the database migrations on start up.
3. Release 0.9.0 will ingore the subdomain related environmental parameters that are no longer needed. We recommend updating your environmental parameters to remove these parameters.

## Installing 0.9.0

Release 0.9.0 simplifies the installation of GovReady-Q by removing the need to manage subdomain-based multi-tenancy.

The installation of assessments (aka "Compliance Apps") requires an extra step in 0.9.0 but greatly improves user experience.


Click one of the tab belows to see quickstart for indicated platform.

.. container:: content-tabs

    .. tab-container:: docker
        :title: Docker

        .. rubric:: Installing with Docker

        Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

        .. rubric:: Start

        .. code-block:: bash

            # Run the docker container in detached mode
            docker container run --name govready-q --detach -p 8000:8000 govready/govready-q-0.9.0.rc

            # Create admin account and organization data if setting up a new database
            # Skip if you have passing environmental variables to connect to a persistent database
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

    .. tab-container:: macos
        :title: macOS

        .. rubric:: Installing on macOS

        GovReady-Q calls requires Python 3.6 or higher to run and several Unix packages to provide full functionality. Install the Homebrew package manager (https://brew.sh) to easily install Unix packages on macOS. Homebrew will install all packages in your userspace and not change native macOS Python or other libraries.

        .. code-block:: bash

            # install Homebrew package manager
            /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

        Now install Python3 and the required Unix packages.

        .. code-block:: bash

            # install dependencies using brew
            brew install python3

            # install other packages: 
            brew install unzip graphviz pandoc selenium-server-standalone magic libmagic
            brew cask install wkhtmltopdf

        .. rubric:: Installing GovReady-Q

        Clone GovReady-Q source code and install.

        .. code-block:: bash

            # clone GovReady-Q
            git clone https://github.com/govready/govready-q
            cd govready-q

            # checkout the 0.9.0.rc (or desired 0.9.0.rc-0xx branch)
            git checkout 0.9.0.rc

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

            # create superuser with initial account if setting up a new database
            # skip if you have passing environmental variables to connect to a persistent database
            python3 manage.py first_run

        .. rubric:: Start GovReady-Q

        .. code-block:: bash

            # run the server
            python3 manage.py runserver

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

            # checkout the 0.9.0.rc (or desired 0.9.0.rc-0xx branch)
            git checkout 0.9.0.rc

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
            # skip if you have passing environmental variables to connect to a persistent database
            python3 manage.py first_run

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

            # checkout the 0.9.0.rc (or desired 0.9.0.rc-0xx branch)
            git checkout 0.9.0.rc

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
            # skip if you have passing environmental variables to connect to a persistent database
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

        Make sure you first install Docker (https://docs.docker.com/docker-for-windows/install/).

        .. rubric:: Start

        .. code-block:: bash

            # Run the docker container in detached mode
            docker container run --name govready-q --detach -p 8000:8000 govready/govready-q-0.9.0.rc

            # Create admin account and organization data
            # Skip if you have passing environmental variables to connect to a persistent database
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

## Adding and Managing AppSources in 0.9.0

Release 0.9.0 reads the compliance apps catalog from the database rather than going to remote repositories and rescanning the local file system each time. The app catalog cache is removed since the page loads much faster.

Release 0.9.0 loads the YAML files into the database when the App Source is first defined. See [App Sources](AppSources.html) for more information about how to configure your instance of GovReady-Q to load apps from local filesystem directories, git repositories (including on-prem git repositories), or GitHub.

The AppSource admin now lists all of the apps provided by the source and has links to import new app versions into the database and to see the app versions already in the database by version number. When the App Source is defined, additional options appear on the database App Source admin page to selectively add individual projects and assessments from the App Source repository to the be published on GovReady-Q. Any time the individual admin page for an App Source is viewed, the App Source is rescanned and new versions of the apps are displayed to be selectively added to be available to users on GovReady-Q.

![screenshot of App Sources list of apps](assets/appsource_apps.png)

When starting a compliance app (i.e. creating a new project), we no longer have to import the app from the remote repository --- instead, we create a new Project and set its root_task to point to a Module in an AppVersion already in the database.

App loading is refactored in a few places. The routines for getting app catalog information from the remote app data are removed since now we only need it for apps already stored in the database.

The AppSource admin's approved app lists form is removed since adding apps into the database is now an administrative function and the database column for it is dropped.

AppVersion now has a boolean field for whether the instance should be included in the compliance apps catalog for users to start new projects with that app.
