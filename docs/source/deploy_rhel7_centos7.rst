Deploying on RHEL 7 / CentOS 7 / Amazon Linux 2
===============================================

Quickstart
----------

.. container:: content-tabs

::

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
           python3 manage.py runserver

       Visit your GovReady-Q site in your web browser at:

           http://localhost:8000/

Additional Details
------------------

.. raw:: html

   <!-- Please update the project's Vagrantfile when revising these instructions. -->

Deployment utilities
~~~~~~~~~~~~~~~~~~~~

Sample ``apache.conf``, ``superviser.ini``, and ``update.sh`` files can
be found in the source code directory ``deployment/rhel``.

Creating a UNIX user named ``govready-q``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may find it useful to create a user specifically for GovReady-Q. Do
this before installing GovReady-Q.

::

   # Create user.
   useradd govready-q -c "govready-q"

   # Change permissions so that Apache can read static files.
   chmod a+rx /home/govready-q

Upgrading pip
~~~~~~~~~~~~~

Upgrade ``pip`` because the RHEL package version is out of date (we need
>=9.1 to properly process hashes in ``requirements.txt``)

::

   pip3 install --upgrade pip

Installing as UNIX user named ``govready-q``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Switch to the govready-q user and install Q:

::

   sudo su govready-q
   cd
   git clone https://github.com/govready/govready-q
   cd govready-q
   git checkout {choose the tag for the current released version}
   pip3 install --user -r requirements.txt
   ./fetch-vendor-resources.sh

Installing drivers for Postgres, MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   # if you intend to use optional configurations, such as the MySQL adapter, you
   # may need to run additional `pip3 install` commands, such as:
   # pip3 install --user -r requirements_mysql.txt
