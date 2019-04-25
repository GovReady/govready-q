# Deploying Q to Red Hat Enterprise Linux 7 / CentOS 7 / Amazon Linux 2

<!-- Please update the project's Vagrantfile when revising these instructions. -->

These instructions can be used to configure a Red Hat Enterprise Linux 7, CentOS 7, or Amazon Linux 2 system to run GovReady-Q.
A Vagrantfile based on CentOS 7 and these instructions is also provided at the root of the GovReady-Q source code.

## Preparing System Packages

GovReady-Q calls out to `git` to fetch apps from git repositories, but that requires git version 2 or later because of the use of the GIT_SSH_COMMAND environment variable. RHEL stock git is version 1. Switch it to version 2+ by using the IUS package:

    # if necessary, enable EPEL and IUS repositories
    rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm https://rhel7.iuscommunity.org/ius-release.rpm

    # if necessary, remove any git currently installed
    yum remove git

    yum install git2u

## Preparing Q Source Code

Create a UNIX user named `govready-q`:

    # Create user.
    useradd govready-q -c "govready-q"
    
    # Change permissions so that Apache can read static files.
    chmod a+rx /home/govready-q

Deploy GovReady-Q source code:

    # Install required software.
    #
    # Note that python36-devel and mysql-devel are needed to compile & install
    # the mysqlclient Python package. But mysql-devl has an installation conflict
    # with IUS. Adding --disablerepo=ius fixes it.
    #
    # gcc is needed to build the uWSGI Python package.
    sudo yum install --disablerepo=ius \
        unzip gcc python36-pip python36-devel \
        graphviz \
        pandoc xorg-x11-server-Xvfb wkhtmltopdf \
        postgresql mysql-devel

Upgrade `pip` because the RHEL package version is out of date (we need >=9.1 to properly process hashes in `requirements.txt`):

    pip3 install --upgrade pip

Then switch to the govready-q user and install Q:

    sudo su govready-q
    cd
    git clone https://github.com/govready/govready-q
    cd govready-q
    git checkout {choose the tag for the current released version}
    pip3 install --user -r requirements.txt
    ./fetch-vendor-resources.sh

    # if you intend to use optional configurations, such as the MySQL adapter, you
    # may need to run additional `pip3 install` commands, such as:
    # pip3 install --user -r requirements_mysql.txt
    
### Test Q with a Local Database

Run the final setup commands to initialize a local Sqlite3 database in `local/db.sqlite` to make sure everything is OK so far:

    python3 manage.py migrate
    python3 manage.py load_modules
    python3 manage.py createsuperuser

And test that the site starts in debug mode at localhost:8000:

	python3 manage.py runserver

## Next steps (Production or Development configuration)

If you're deploying GovReady-Q to a production environment, see the [Production deployment steps](deploy_prod.html).

If you're deploying GovReady-Q for development or evaluation purposes, [Development deployment steps](deploy_local_dev.html) may be useful for you.
