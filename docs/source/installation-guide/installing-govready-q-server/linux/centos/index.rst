.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_sources_centos_rhel:

CentOS / RHEL 7 from sources
============================

This guide describes how to install the GovReady-Q server for CentOS 7 or greater from source code.
This guide will take you through the following steps:

1. Installing required OS packages
2. Cloning the GovReady-Q repository
3. Installing desired database
4. Creating the local/environment.json file
5. Installing GovReady-Q
6. Starting and stopping GovReady-Q
7. Running GovReady-Q with Gunicorn HTTP WSGI
8. Monitoring GovReady-Q with Supervisor
9. Using NGINX as a reverse proxy
10. Additional options

1. Installing required OS packages
----------------------------------

GovReady-Q requires Python 3.6 or higher and several Linux packages to
provide full functionality. Execute the following commands:

.. code:: bash

   # Enable IUS repository
   sudo yum install https://centos7.iuscommunity.org/ius-release.rpm
   sudo yum update

   # Install dependencies
   sudo yum install \
   python36u python36u-pip \
   unzip git2u jq \
   graphviz pandoc

   # Upgrade pip to version 20.1+
   python3 -m pip install --upgrade pip

   # Optionally install supervisord for monitoring and restarting GovReady-q; and NGINX as a reverse proxy
   DEBIAN_FRONTEND=noninteractive \
   apt-get install -y supervisor nginx

   # To generate thumbnails and PDFs for export, you must install wkhtmltopdf
   # WARNING: wkhtmltopdf can expose you to security risks. For more information,
   # search the web for "wkhtmltopdf Server-Side Request Forgery"
   read -p "Are you sure (yes/no)? " ; if [ "$REPLY" = "yes" ]; then sudo yum install xorg-x11-server-Xvfb wkhtmltopdf ; fi

GovReady-Q calls out to ``git`` to fetch apps from git repositories, but
that requires git version 2 or later because of the use of the
GIT_SSH_COMMAND environment variable. The stock git on RHEL is version 1.
Switch it to version 2+ by using the IUS package:

.. code:: bash

   # If necessary, remove any git currently installed
   sudo yum remove git

   # Install git2u
   sudo yum install git2u


Upgrading pip on RHEL 7
~~~~~~~~~~~~~~~~~~~~~~~

Upgrade ``pip`` because the RHEL package version is out of date (we need
>=9.1 to properly process hashes in ``requirements.txt``)

.. code:: bash

   pip3 install --upgrade pip

2. Cloning the GovReady-Q repository
------------------------------------

You now need to decide where to install the GovReady-Q files and whether to run GovReady-Q as root or as a dedicated
Linux user. Installing as root is convenient for initial testing and some circumstances. Creating a dedicated user and installing as that user is considered better practice.

2 (option a). Installing as root
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   These steps assume your are installing into the ``/opt/`` directory as root.

Clone the GovReady-Q repository from GitHub into the desired directory on your Ubuntu server.

.. code:: bash

   cd /opt

   # Clone GovReady-Q
   git clone https://github.com/govready/govready-q /path/to/govready-q
   cd govready-q

   # GovReady-Q files are now installed in /opt/govready-q and owned by root

2 (option b). Installing as Linux user "govready-q"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   These steps assume your are installing into the ``/home/govready-q`` directory as user ``govready-q``.

While you are still root, create a dedicated Linux user ``govready-q`` and home directory. Change directory into the
created user's home directory and switch users to ``govready-q``. Clone the GovReady-Q repository from GitHub.

.. code:: bash

   # Create user
   useradd govready-q -m -c "govready-q"
   chsh -s /bin/bash govready-q
   cp /etc/skel/.bashrc /home/govready-q/.
   chown govready-q:govready-q /home/govready-q/.bashrc

   # Change permissions so that the webserver can read static files
   chmod a+rx /home/govready-q

   # Switch to the govready-q user
   cd /home/govready-q
   su govready-q

   # Clone GovReady-Q
   git clone https://github.com/govready/govready-q
   cd govready-q

   # GovReady-Q files are now installed in /home/govready-q/govready-q and owned govready-q

3. Installing desired database
------------------------------

GovReady-Q requires a relational database. You can choose:

* SQLITE3
* MySQL
* PostgreSQL

GovReady-Q will automatically default to and use a SQLITE3 database installed at ``local/db.sqlite3``
if you do not specify a database connection string in ``local/environment.json``.

3 (option a). Installing SQLITE3 (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no setup necessary to use SQLITE3. GovReady-Q will automatically install a local SQLITE3 database
``local/db.sqlite3`` by default if no ``db`` parameter is set in ``local/environment.json``.

.. note::
   All files in ``govready-q/local`` are git ignored so that you can safely pull git updates.

3 (option b). Installing MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the database server, install MySQL OS packages:

.. code:: bash

   # Install of MySQL OS packages
    sudo yum install -y mysql-devel

Make a note of the MySQL's host, port, database name, user and password to add to GovReady-Q's configuration file at ``local/environment.json``.

.. code:: json

   {
      ...
      "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
      ...
   }


3 (option c). Installing PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the database server, install PostgreSQL OS packages:

.. code:: bash

   sudo apt install -y postgresql postgresql-contrib
   # postgresql-setup initdb

Then set up the user and database (both named ``govready_q``):

.. code:: bash

   sudo -iu postgres createuser -P govready_q
   # Paste a long random password when prompted

   sudo -iu postgres createdb govready_q

Postgres’s default permissions automatically grant users access to a
database of the same name.

You must specify the database connection string in GovReady-Q's configuration file at ``local/environment.json``.

Make a note of the Postgres host, port, database name, user and password to add to GovReady-Q's configuration file at ``local/environment.json``.

.. code:: json

   {
      ...
      "db": "postgres://USER:PASSWORD@HOST:PORT/NAME",
      ...
   }

**Encrypting your connection to PostgreSQL running on a separate database server**

If PostgreSQL is running on a separate host, it is highly recommended you follow the below instructions
to configure a secure connection between GovReady-Q and PostgreSQL.

In ``/var/lib/pgsql/data/postgresql.conf``, enable TLS connections by
changing the ``ssl`` option to

::

   ssl = on 

and enable remote connections by binding to all interfaces:

::

   listen_addresses = '*'

Enable remote connections to the database *only* from the webapp server
and *only* encrypted with TLS by editing
``/var/lib/pgsql/data/pg_hba.conf`` and adding the line (replacing the
hostname with the hostname of the Q webapp server):

::

   hostssl all all webserver.example.com md5

Generate a self-signed certificate (replace ``db.govready-q.internal``
with the database server’s hostname if possible):

::

   openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /var/lib/pgsql/data/server.key -out /var/lib/pgsql/data/server.crt -subj '/CN=db.govready-q.internal'
   chmod 600 /var/lib/pgsql/data/server.{key,crt}
   chown postgres.postgres /var/lib/pgsql/data/server.{key,crt}

Copy the certificate to the webapp server so that the webapp server can
make trusted connections to the database server:

.. code:: bash

   cat /var/lib/pgsql/data/server.crt
   # Place on webapp server at /home/govready-q/pgsql.crt

Restart the PostgreSQL:

.. code:: bash

   service postgresql restart

And if necessary, open the PostgreSQL port:

.. code:: bash

   firewall-cmd --zone=public --add-port=5432/tcp --permanent
   firewall-cmd --reload

4. Creating the local/environment.json file
-------------------------------------------

Create the ``local/environment.json`` file with appropriate parameters. (Order of the key value pairs is not significant.)

**SQLITE (default)**

.. code:: json

      {
         "govready-url": "http://localhost:8000",
         "debug": false,
         "secret-key": "long_random_string_here"
      }

**MySQL**

.. code:: json

      {
         "db": "mysql://USER:PASSWORD@localhost:PORT/NAME",
         "govready-url": "http://localhost:8000",
         "debug": false,
         "secret-key": "long_random_string_here"
      }

**PostgreSQL**

.. code:: json

      {
         "db": "postgres://govready_q:PASSWORD@localhost:5432/govready_q",
         "govready-url": "http://localhost:8000",
         "debug": false,
         "secret-key": "long_random_string_here"
      }


.. note::
   As of 0.9.1.20, the "govready-url" environment parameter is preferred way to set Django internal security, url,
   ALLOWED_HOST, and other settings instead of deprecated environment parameters "host" and "https".
   The "host" and "https" deprecated parameters will continue to be support for reasonable period for legacy installs.

   Deprecated (but supported for a reasonable period):

   .. code:: json

      {
         "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
         "host": "localhost:8000",
         "https": false,
         "debug": false,
         "secret-key": "long_random_string_here"
      }

   Preferred:

   .. code:: json

      {
         "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
         "govready-url": "http://localhost:8000",
         "debug": false,
         "secret-key": "long_random_string_here"
      }

   See `Environment Settings <Environment.html>`__ for a complete list of configuration options.

5. Installing GovReady-Q
------------------------

At this point, you have installed required OS packages; cloned the GovReady-Q repository; configured your preferred database option of SQLITE3, MySQL, or PostgreSQL; and created the ``local/environment.json`` file with appropriate settings.

Make sure you are in the base directory of the GovReady-Q repository. (Execute the following commands as the dedicated Linux user if you set one up.)

Run the install script to install required Python libraries, initialize GovReady-Q's database and create a superuser. This is the same command for all database backends.

.. code:: bash

   # If you created a dedicated Linux user, be sure to switch to that user to install GovReady-Q
   # su govready-q
   # cd /home/govready-q/govready-q

   # Run the install script to install Python libraries,
   # intialize database, and create Superuser
   ./install-govready-q

.. note::
   The command ``install-govready-q.sh`` creates the Superuser interactively allowing you to specify username and password.

   The command ``install-govready-q.sh --non-interactive`` creates the Superuser automatically for installs where you do
   not have access to interactive access to the commandline. The auto-generated username and password will be generated once to the standout log.

6. Starting and stopping GovReady-Q
-----------------------------------

**Starting GovrReady-Q**

You can now start GovReady-Q Server. GovReady-Q defaults to listening on localhost:8000, but can easily be run to listen on other host domains and ports.

.. code:: bash

   # Run the server on the default localhost and port 8000
   python3 manage.py runserver

Visit your GovReady-Q site in your web browser at: http://localhost:8000/

.. code:: bash

   # Run the server to listen at a different specific host and port
   # python manage.py runserver host:port
   python3 manage.py runserver 0.0.0.0:8000
   python3 manage.py runserver 67.205.167.168:8000
   python3 manage.py runserver example.com:8000

**Stopping GovReady-Q**

Press ``CTL-c`` in the terminal window running GovReady-Q to stop the server.

7. Running GovReady-Q with Gunicorn HTTP WSGI
---------------------------------------------

In this step, you will configure your deployment to use a higher performing, multi-threaded gunicorn (Green Unicorn) HTTP WSGI server
instead of GovReady-Q using Django's built-in server. This will serve you pages faster, with greater scalability.
You will start gunicorn server using a config file which has settings to start GovReady-Q.

8. Monitoring GovReady-Q with Supervisor
----------------------------------------

In this step, you will configure your deployment to use Supervisor to monitor and restart Gunicorn automatically if GovReady-Q
should unexpectedly crash.

9. Using NGINX as a reverse proxy
---------------------------------

In this step, you will configure your deployment to use NGINX as a reverse proxy in front of Gunicorn as an extra layer of performance and security. 

10. Additional options
----------------------

Installing GovReady-Q Server command-by-command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For situations in which more granular control over the install process is required, use the below sequence of commands for installing GovReady-Q.

.. code:: bash

   # Clone GovReady-Q
   git clone https://github.com/govready/govready-q
   cd govready-q

   # Install Python 3 packages
   pip3 install --user -r requirements.txt

   # Install Bootstrap and other vendor resources locally
   ./fetch-vendor-resources.sh

   # Initialize the database by running database migrations (sqlite3 database used by default)
   python3 manage.py migrate

   # Load a few critical modules
   python3 manage.py load_modules

   # Create superuser with initial account interactively with prompts
   python3 manage.py first_run
   # Reply to prompts interactively

   # Alternatively, create superuser with initial account non-interactively
   # python3 manage.py first_run --non-interactive
   # Find superuser name and password in output log

.. note::
   The command ``python3 manage.py first_run`` creates the Superuser interactively allowing you to specify username and password.

   The command ``python3 manage.py first_run --non-interactive`` creates the Superuser automatically for installs where you do
   not have access to interactive access to the commandline. The auto-generated username and password will be generated once to
   to the standout log.


Enabling PDF export
~~~~~~~~~~~~~~~~~~~

To activate PDF and thumbnail generation, add ``gr-pdf-generator`` and
``gr-img-generator`` environment variables to your
``local/environment.json`` configuration file:

.. code:: json

   {
      ...
      "gr-pdf-generator": "wkhtmltopdf",
      "gr-img-generator": "wkhtmltopdf",
      ...
   }

Deployment utilities
~~~~~~~~~~~~~~~~~~~~

GovReady-Q can be optionally deployed with NGINX and Supervisor. There's also a script for updating GovReady-Q.

Sample ``nginx.conf``, ``supervisor.confg``, and ``update.sh`` files can
be found in the source code directory ``deployment/ubuntu``.

Notes
=====

Instructions applicable for RHEL 7 and CentOS 7 and tested on a `CentOS 7.8.2003 Docker image <https://hub.docker.com/_/centos>`__.
