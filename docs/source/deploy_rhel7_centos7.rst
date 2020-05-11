Deploying on RHEL 7 or CentOS 7
================================

*Instructions applicable for RHEL 7 and CentOS 7. Tested
on a*
`CentOS 7.8.2003 Docker image <https://hub.docker.com/_/centos>`__
*of 2020-05-04.*

Installation on RHEL/CentOS 7
-----------------------------

GovReady-Q requires Python 3.6 or higher and several Linux packages to
provide full functionality. Execute the following commands:

.. code:: bash

   # enable IUS repository
   sudo yum install https://centos7.iuscommunity.org/ius-release.rpm
   sudo yum update

   # install dependencies
   sudo yum install \
   python36u python36u-pip \
   unzip git2u jq nmap-ncat \
   graphviz pandoc

   # to generate thumbnails and PDFs for export, you must install wkhtmltopdf
   # WARNING: wkhtmltopdf can expose you to security risks. For more information,
   # search the web for "wkhtmltopdf Server-Side Request Forgery"
   read -p "Are you sure (yes/no)? " ; if [ "$REPLY" = "yes" ]; then sudo yum install xorg-x11-server-Xvfb wkhtmltopdf ; fi

GovReady-Q calls out to ``git`` to fetch apps from git repositories, but
that requires git version 2 or later because of the use of the
GIT_SSH_COMMAND environment variable. The stock git on RHEL is version 1.
Switch it to version 2+ by using the IUS package:

.. code:: bash

   # if necessary, remove any git currently installed
   sudo yum remove git

   # install git2u
   sudo yum install git2u

Install GovReady
~~~~~~~~~~~~~~~~

Clone the GovReady source code and install packages.

.. code:: bash

   # clone GovReady-Q
   git clone https://github.com/govready/govready-q
   cd govready-q

   # install Python 3 packages
   pip3 install --user -r requirements.txt

   # install Bootstrap and other vendor resources locally
   # (sudo needed only for the embedded 'yum install' command)
   sudo ./fetch-vendor-resources.sh

Set up GovReady
~~~~~~~~~~~~~~~

Run the final setup commands to initialize a local SQLite database in
local/db.sqlite to make sure everything is OK so far.

The following warning message is expected and okay:

   **WARNING: Specified PDF generator is not supported. Setting generator
   to ‘off’.**

.. code:: bash

   # run database migrations (sqlite3 database used by default)
   python3 manage.py migrate

   # load a few critical modules
   python3 manage.py load_modules

   # create superuser with initial account
   python3 manage.py first_run

Start GovReady
~~~~~~~~~~~~~~

.. code:: bash

   # run the server
   python3 manage.py runserver 0.0.0.0:8000

Visit your GovReady-Q site in your web browser at:

http://localhost:8000/

Additional Details
------------------

Manual installation on a Docker container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have experience with Docker and want to try this manual
installation without affecting your own computer, you can run a CentOS 7
container with these commands.

.. code:: bash

   # start a container, forward port 8000 for GovReady
   docker run -it --name govready-q -p8000:8000 centos:7.8.2003 bash

You will start in a root shell. Create a non-root user:

.. code:: bash

   # create user and set password
   adduser testuser
   passwd testuser

   # give test user sudo privileges
   usermod -aG wheel testuser

   # add 'sudo' command
   yum install sudo

   # switch to the testuser account
   su - testuser

Then you can proceed from the top of this document as the non-root user
``testuser``.

Creating “environment.json” configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GovReady uses a configuration file stored at ``local/environment.json``.

See `Environment Settings <Environment.html>`__ for a complete list of variables you can
configure.

Create a file there and include values like these:

.. code:: json

   {
     "debug": false,
     "host": "localhost:8000",
     "https": false,
     "secret-key": "...something here..."
   }

Enabling PDF export
~~~~~~~~~~~~~~~~~~~

To activate PDF and thumbnail generation, add ``gr-pdf-generator`` and
``gr-img-generator`` environment variables to your
``local/environment.json`` configuration file:

::

   {
      ...
      "gr-pdf-generator": "wkhtmltopdf",
      "gr-img-generator": "`wkhtmltopdf",
      ...
   }

Deployment utilities
~~~~~~~~~~~~~~~~~~~~

Sample ``apache.conf``, ``superviser.ini``, and ``update.sh`` files can
be found in the source code directory ``deployment/rhel``.

Creating a dedicated GovReady UNIX user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may find it useful to create a user specifically for GovReady-Q. Do
this before installing GovReady-Q.

.. code:: bash

   # Create user.
   useradd govready-q -c "govready-q"

   # Change permissions so that the webserver can read static files.
   chmod a+rx /home/govready-q

Optional install of database engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # optional install of postgres and/or mysql
   sudo yum install postgresql mysql-devel

Installing drivers for Postgres, MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # if you intend to use optional configurations, such as the MySQL adapter, you
   # may need to run additional `pip3 install` commands, such as:
   # pip3 install --user -r requirements_mysql.txt

Upgrading pip
~~~~~~~~~~~~~

Upgrade ``pip`` because the RHEL package version is out of date (we need
>=9.1 to properly process hashes in ``requirements.txt``)

.. code:: bash

   pip3 install --upgrade pip

