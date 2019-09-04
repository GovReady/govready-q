# Version 0.9.0

## What's New in 0.9.0

Release 0.9.0 (coming July 2019) is a minor release improving
the user experience and performance.

* Faster loading and launching of Assessments/questionnaires
* Simplified install with no subdomains to worry about
* Replaces subdomain multi-tenancy with simplified "Groups" model
* Improved authoring screens
* Helpful new start page

Release 0.9.0 removes multi-tenancy and serves all pages from the same domain. In the earlier multi-tenancy versions, requests to GovReady-Q came in on subdomains: the subdomain determined which organization to associate with the request, and individuals had to re-login across subdomains. Little value was being realized by actual users for the subdomain-based multi-tenancy. Removing subdomain-based multi-tenancy reduces technical debt simplifies deployment.

This release's compliance apps catalog now reads from the database rather than constantly rescanning remote repositories and the file system. The app catalog cache is removed since the page loads much faster. Release 0.9.0 begins to replace the "compliance app" terminology with the plain language "projects" and "assessment" terminology in end user pages.

This release also introduces a "Group" feature to organize and manage related projects.

For a complete list of changes see the [0.9.0.dev branch CHANGELOG](https://github.com/GovReady/govready-q/blob/0.9.0.dev/CHANGELOG.md).

Release 0.9.0 progress can be found on the `0.9.0.dev` and `0.9.0.rc-xxx` branches.

## 0.9.0 vs 0.8.6 Screenshots

**0.9.0 vs 0.8.6: Sign-in Page**
<!-- ![0.9.0 Sign-in Page](assets/090_sign_in.png) -->

<!-- ![0.8.6 Sign-in Page](assets/086_sign_in.png) -->

<table border="0">
    <tr> 
        <th> 0.8.6 (Old Version) </th> 
        <th> 0.9.0 (New Version) </th>
    </tr>
    <tr>
        <td><img src="assets/086_sign_in.png" width="480" /></td> 
        <td><img src="assets/090_sign_in.png" width="480" /></td>
    </tr>
</table> 

**0.9.0 vs 0.8.6: Project Page**
![0.9.0 Project Page](assets/090_project_page.png)

![0.8.6 Project Page](assets/086_project_page.png)

**0.9.0 vs 0.8.6: New Portfolios vs Old Compliance Apps**
![0.9.0 Portfolios](assets/090_porfolio_1.png)
![0.9.0 Portfolios continued](assets/assets/090_porfolio_2.png)

![0.8.6 Old Compliance Apps](assets/086_compliance_app.png)

**0.9.0 vs 0.8.6: Module View**
![0.9.0 Module](assets/090_module_view.png)

![0.8.6 Module](assets/assets/086_module_view.png)

**0.9.0 Feature Showcase**
![Retooled Form Interface](assets/090_retooled_form.png)
![Permissions Settings](assets/090_permissions_settings.png)
![Help Squad](assets/090_help_squad.png)
![API Keys Screen](assets/090_api_keys.png)


## Release Date

The target release date 0.9.0 is July 2019.

## Installing 0.9.0

Release 0.9.0 simplifies the installation of GovReady-Q by removing the need to manage subdomain-based multi-tenancy.

Three example assessments are preloaded during the install of 0.9.0 to demonstrate the experience of using GovReady-Q.

Click one of the tab belows to see the release 0.9.0 quickstart for the indicated platform.

.. container:: content-tabs

    .. tab-container:: docker
        :title: Docker

        .. rubric:: Installing with Docker

        Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

        .. code-block:: bash

            # Run the govready-q-0.9.0 docker container in detached mode
            # Note this is a multi-line command
            # This command uses port 8000, please make sure this port is free before running 
            docker container run --detach --name govready-q-0.9.0 -p 127.0.0.1:8000:8000 \
            -e HOST=localhost -e PORT=8000 -e HTTPS=false -e DBURL= -e DEBUG=true \
            govready/govready-q-0.9.0

            # Create admin account and organization data if setting up a new database
            docker container exec -it govready-q-0.9.0 first_run

            # Stop, start container (when needed)
            docker container stop govready-q-0.9.0
            docker container start govready-q-0.9.0

            # View logs - useful if site does not appear
            docker container logs govready-q-0.9.0

            # To destroy the container and all user data entered into Q
            docker container rm -f govready-q-0.9.0

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

        Dockerized GovReady-Q supports additional options. Below is a more complete example
        parameters available, including mounting a local directory to author your own assessments.

        .. code-block:: bash

            # Create a local directory for authoring Q assessment files
            cd ~/
            mkdir govready-q-workspace
            cd govready-q-workspace

            # Run the govready-q-0.9.0 docker container in detached mode
            # mounting your present working directory.
            # Additional parameters for configuring email also shown.
            docker container run --detach --name govready-q-0.9.0 -p 127.0.0.1:8000:8000 \
            -e HOST=localhost -e PORT=8000 -e HTTPS=false -e DBURL= -e DEBUG=true \
            -e EMAIL_HOST= -e EMAIL_PORT= -e EMAIL_USER= -e EMAIL_PW= -e EMAIL_DOMAIN= \
            --mount type=bind,source="$(pwd)",target=/mnt/q-files-host \
            govready/govready-q-0.9.0

            # Create admin account and organization data if setting up a new database
            docker container exec -it govready-q-0.9.0 first_run

            # To destroy the container and all user data entered into Q
            docker container rm -f govready-q-0.9.0

        Alternatively, we offer a shell script that helps launch GovReady-Q.
        Do the following to download the shell script and launch GovReady-Q docker container.

        .. code-block:: bash

            cd /path/to/working/dir

            # Get the docker_container_run.sh shell script
            wget https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh

            # Make it executable
            chmod +x docker_container_run.sh

            ./docker_container_run.sh --name govready-q-0.9.0 --relaunch --debug -v --appsdevdir /codedata/code/govready-q-files --image govready/govready-q-0.9.0

        .. rubric:: Logs for Debugging

        The container's console shows the output of container's start-up commands including database migrations and process startup. The container's console log can be accessed with

        .. code-block:: bash

            docker container logs govready-q-0.9.0

        GovReady-Q application logs can be found in `/var/log` within the container to track status and assist with debugging. These files contain access logs and other program output.

        * `/var/log/application-stderr.log` - GovReady-Q application standard error
        * `/var/log/application-stdout.log` - GovReady-Q application standard out
        * `/var/log/notificationemails-stderr.log` - GovReady-Q email notifications standard error
        * `/var/log/notificationemails-stdout.log` - GovReady-Q email notifications standard error
        * `/var/log/supervisord.log` - Supervisor daemon

        .. rubric:: Debugging "Internal Server Error" Messages

        A special management command can be used to see the application log files to debug unhandled  "Internal Server Error" (HTTP code 500) messages displayed in the browser to end users 

        .. code-block:: bash

            docker container exec govready-q-0.9.0 tail_logs
            # Replace "govready-q-0.9.0" with name of your container or use container id

        `tail_logs` takes the same arguments as Unix `tail`. For instance, add `-n 1000` to see the most recent 1,000 log lines, or add `-f` to continue to output the logs as the log files grow.

        .. code-block:: bash

            # most recent 200 lines of logs
            docker container exec govready-q-0.9.0 tail_logs -n 200

            # real-time display of logs
            docker container exec govready-q-0.9.0 tail_logs -f

        The log files can also be accessed by mounting `/var/log` with a Docker bind-mount or as a volume (and that's the only way to see the logs if `docker container exec` cannot be used in your environment).

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

            # checkout the 0.9.0.dev (or desired 0.9.0.rc-0xx branch)
            git checkout 0.9.0.dev

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
            # skip if you pass environment variables to connect to a persistent database
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

            # checkout the 0.9.0.dev (or desired 0.9.0.rc-0xx branch)
            git checkout 0.9.0.dev

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
            # skip if you pass environment variables to connect to a persistent database
            python3 manage.py first_run

            python3 manage.py first_run

        .. rubric:: Start GovReady-Q

        .. code-block:: bash

            # run the server
            python3 manage.py runserver

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

            # checkout the 0.9.0.dev (or desired 0.9.0.rc-0xx branch)
            git checkout 0.9.0.dev

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
            # skip if you pass environment variables to connect to a persistent database
            python3 manage.py first_run

        .. rubric:: Start GovReady-Q

        .. code-block:: bash

            # run the server
            python3 manage.py runserver

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

    .. tab-container:: windows
        :title: Windows

        .. rubric:: Installing with Docker

        Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

        .. code-block:: bash

            # Run the govready-q-0.9.0 docker container in detached mode
            docker container run --detach --name govready-q-0.9.0 -p 127.0.0.1:8000:8000 \
            -e HOST=localhost -e PORT=8000 -e HTTPS=false -e DBURL= -e DEBUG=true \
            govready/govready-q-0.9.0

            # Create admin account and organization data if setting up a new database
            docker container exec -it govready-q-0.9.0 first_run

            # Stop, start container (when needed)
            docker container stop govready-q-0.9.0
            docker container start govready-q-0.9.0

            # View logs - useful if site does not appear
            docker container logs govready-q-0.9.0

            # To destroy the container and all user data entered into Q
            docker container rm -f govready-q-0.9.0

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

        Dockerized GovReady-Q supports additional options. Below is a more complete example
        parameters available, including mounting a local directory to author your own assessments.

        .. code-block:: bash

            # Create a local directory for authoring Q assessment files
            cd ~/
            mkdir govready-q-workspace
            cd govready-q-workspace

            # Run the govready-q-0.9.0 docker container in detached mode
            # mounting your present working directory.
            # Additional parameters for configuring email also shown.
            docker container run --detach --name govready-q-0.9.0 -p 127.0.0.1:8000:8000 \
            -e HOST=localhost -e PORT=8000 -e HTTPS=false -e DBURL= -e DEBUG=true \
            -e EMAIL_HOST= -e EMAIL_PORT= -e EMAIL_USER= -e EMAIL_PW= -e EMAIL_DOMAIN= \
            --mount type=bind,source="$(pwd)",target=/mnt/q-files-host \
            govready/govready-q-0.9.0

            # Create admin account and organization data if setting up a new database
            docker container exec -it govready-q-0.9.0 first_run

            # To destroy the container and all user data entered into Q
            docker container rm -f govready-q-0.9.0

        Alternatively, we offer a shell script that helps launch GovReady-Q.
        Do the following to download the shell script and launch GovReady-Q docker container.

        .. code-block:: bash

            cd /path/to/working/dir

            # Get the docker_container_run.sh shell script
            wget https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh

            # Make it executable
            chmod +x docker_container_run.sh

            ./docker_container_run.sh --name govready-q-0.9.0 --relaunch --debug -v --appsdevdir /codedata/code/govready-q-files --image govready/govready-q-0.9.0


## Upgrading to 0.9.0 from 0.8.x

**Backup your database before upgrading to 0.9.0. Release 0.9.0 performs database changes that makes rolling back difficult.**

If you are installing from source code:
1. Pull and use the [0.9.0.dev branch](https://github.com/GovReady/govready-q/tree/0.9.0.dev).
2. Tell Django to run the database migrations (e.g., `python manage.py migrate`).
3. We recommend updating to your `local/environment.json` file to address release 0.9.0's removal of the need to manage subdomain-based multi-tenancy.

If you are installing using Docker:
1. Make sure you pull the [0.9.0 container](https://cloud.docker.com/u/govready/repository/docker/govready/govready-q-0.9.0).
2. If you are using environment variables to connect the Docker deployment to a persistent database, GovReady-Q will automatically run the database migrations on start up.
3. Release 0.9.0 will ignore the subdomain-related environment variables that are no longer needed. We recommend updating your environment variables to remove them.

## Adding and Managing "Compliance Apps" in 0.9.0

### Overview

Version 0.9.0 includes three assessments preloaded for demonstration purposes.

GovReady-Q must be configured by an administrator to load compliance assessments from one or more sources, which can be local directories or remote git repositories. Full administrative privileges are assigned to original user account created when executing `python manage.py first_run` during installation.

App Sources are configured in the Django admin at the URL `/admin` on your GovReady-Q domain under `App Sources`:

![App Sources list](assets/appsources_list.png)

Each App Source points GovReady-Q to a directory or repository of compliance apps.

![Example App Source](assets/appsource_git_https.png)

### App Source Slug

The first App Source field is the Slug. The Slug is a short name you assign to the App Source to distinguish it from other App Sources. The Slug is used to form URLs in GovReady-Q's compliance apps catalog, so it may only contain letters, numbers, dashes, underscores, and other URL path-safe characters.

### App Source Type

There are four types of App Sources: local directories, remote git repositories using HTTP which are typically public repositories, remote git repositories using SSH which typically use SSH deploy keys for access, and remote GitHub repositories using a GitHub username and password for access.

#### Local Directory

The Local Directory source type directs GovReady-Q to load compliance apps from a directory on the same machine GovReady-Q is running on. (When deploying with Docker, that's on the container filesystem unless a path has been mounted to a volume or to the host machine.)

In the `Path` field, enter the path to a local directory containing compliance apps. This path is expected to contain a sub-directory for each compliance app contained in this source. For instance, if you have this directory layout:

    .
    └── home
        └── user
            └── compliance_apps
                ├── myfirstapp
                │   └── app.yaml
                └── mysecondapp
                    └── app.yaml

then your Path would be `/home/user/compliance_apps`.

The path can be absolute or relative to the path in which GovReady-Q is installed.

#### Git Repository over HTTPS

The Git Repository over HTTPS source type is for git repositories, such as on GitHub or GitLab, that can be cloned using an HTTPS URL. These repositories are typically public, or in an enterprise environment public within your organization's network.

Paste the HTTPS git clone URL --- such as https://github.com/GovReady/govready-apps-dev --- into the URL field. Here's what that looks like:

![App Source for a public git repository](assets/appsource_git_https.png)

The other fields can be left blank.

The `Path` field optionally specifies a sub-directory within the repository in which the compliance apps are stored if they are not stored in the root of the repository. For instance if the repository has a directory layout similar to:

    .
    └── github.com/organization/repository
        └── apps
            ├── myfirstapp
            │   └── app.yaml
            └── mysecondapp
                └── app.yaml

then set the `Path` field to `apps`.

If the compliance apps are not in the repository's default branch (i.e. something other than the typical `master` default branch), then set the `Branch` field to the name of the branch to read the compliance apps from.

You can use HTTPS to access private repositories by placing your username and password or [personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) into the URL, such as:

    https://username:password@github.com/GovReady/govready-apps-dev

Since this requires user credentials, it should be avoided for production deployments in favor of using Git Repository over SSH (see below).

#### Git Repository over SSH

If your git repository is private and accessible using an SSH URL (which typically looks like git@github.com:organization/repository.git) and an SSH public/private keypair, such as with GitHub or GitLab deploy keys, then use the Git Repository over SSH source type.

Create a new SSH key for your GovReady-Q instance to be used as a deploy key:

    ssh-keygen -q -t rsa -b 2048 -N "" -C "_your-repo-name_-deployment-key" -f ./repo_deploy_key

Your GovReady-Q instance will hold the private key half of the newly generated keypair, and your source code control system will hold the public key.

Back in the Django admin, set the Source Type to Git Repository over SSH. Paste the git clone SSH URL into the URL field. Then open the newly generated file `repo_deploy_key` and paste its contents into the SSH Key field. Here's what that looks like:

![App Source for a private git repository](assets/appsource_git_ssh.png)

The other fields can be left blank. `Path` and `Branch` can be set the same as with the Git Repository over HTTPS source type (see above).

Copy the public key in the newly generated file `repo_deploy_key.pub` into the deploy keys section of your source code repository. Here is what that looks like on GitHub:

![Adding a deploy key to GitHub](assets/github_deploy_key_add.png)

Make the key read only by leaving "Allow write access" field unchecked and click `Add the key` to save the key.

#### GitHub Repository using the GitHub API

This source type can be used to access private GitHub repositories using a GitHub username and password or a username and [personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/).

Set the `Repository` field to the organization name and repository name, separated by a slash, as in the repository's URL following `github.com/`. In `Other Parameters`, paste a small YAML-formatted document holding a GitHub username and password or username and personal access token, formatted as follows:

    auth:
      user: 'myusername'
      pw: 'mypassword'

The other fields can be left blank. `Branch` can be set the same as with the Git Repository over HTTPS source type (see above).

Since this source type requires user credentials, it should be avoided for production deployments in favor of using Git Repository over SSH.

### Compliance Apps

Compliance Apps are the actual assessments and questionnaires, the "data packs", that drive GovReady-Q.

The AppSource admin now lists all of the apps provided by the source and has links to import new app versions into the database and to see the app versions already in the database by version number. When the App Source is defined, additional options appear on the database App Source admin page to selectively add individual projects and assessments from the App Source repository to the be published on GovReady-Q. Any time the individual admin page for an App Source is viewed, the App Source is rescanned and new versions of the apps are displayed to be selectively added to be available to users on GovReady-Q.

![screenshot of App Sources list of apps](assets/appsource_apps.png)

When starting a compliance app (i.e. creating a new project), we no longer have to import the app from the remote repository --- instead, we create a new Project and set its root_task to point to a Module in an AppVersion already in the database.

App loading is refactored in a few places. The routines for getting app catalog information from the remote app data are removed since now we only need it for apps already stored in the database.

The AppSource admin's approved app lists form is removed since adding apps into the database is now an administrative function and the database column for it is dropped.

AppVersion now has a boolean field for whether the instance should be included in the compliance apps catalog for users to start new projects with that app.
