.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_sources_ubuntu:

Ubuntu from sources
===================

This guide describes how to install the GovReady-Q server for Ubuntu 16.04 or greater from source code.

1. Installing required OS packages
-------------------------------

GovReady-Q requires Python 3.6 or higher and several Linux packages to
provide full functionality. Execute the following commands as root:

.. code:: bash

   # Update package list
   apt-get update

   # Install dependencies
   DEBIAN_FRONTEND=noninteractive \
   apt-get install -y \
   unzip git curl \
   python3 python3-pip \
   python3-yaml \
   graphviz pandoc \
   language-pack-en-base language-pack-en

   # Upgrade pip to version 20.1+
   python3 -m pip install --upgrade pip

   # To optionally generate thumbnails and PDFs for export, you must install wkhtmltopdf
   # WARNING: wkhtmltopdf can expose you to security risks. For more information,
   # search the web for "wkhtmltopdf Server-Side Request Forgery"
   read -p "Are you sure you need to generate PDF files (yes/no)? " ; if [ "$REPLY" = "yes" ]; then apt-get install wkhtmltopdf ; fi

.. warning::
   The default version 9.0.x of pip installed on Ubuntu (May 2020) correctly installs Python packages when run as root, but fails when run as non-root user and does not report the error clearly. (Pip 9.0.x fails to create the user's ``.local`` directory for installing the packages.)
   Upgrading pip to version 20.x solves this problem. Pip must be upgraded to 20.x for the ``./install-govready-q`` script to properly install the
   Python packages.

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

GovReady-Q will automatically default to and use a SQLITE3 database
if you do not specify a database connection string in ``local/environment.json``.



3 (option a). Installing SQLITE3 (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no setup necessary to use SQLITE3. GovReady-Q will automatically install a local SQLITE3 database
``local/db.sqlite3`` by default if no ``db`` parameter is set in ``local/environment.json``.

.. note::
   All files in ``govready-q/local`` are git ignored so that you can safely pull git updates.


3 (option b). Installing MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install MySQL OS packages either the same server as GovReady-Q or on a different database server.

.. code:: bash

   # Install of MySQL OS packages
   sudo apt-get install -y mysql-server mysql-client

.. code:: bash

   # If you intend to use optional configurations, such as the MySQL adapter, you
   # may need to run additional `pip3 install` commands, such as:
   pip3 install --user -r requirements_mysql.txt

Make a note of the MySQL's host, port, database name, user and password to add to GovReady-Q's configuration file at ``local/environment.json``.

.. code:: json

   {
      ...
      "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
      ...
   }

3 (option c). Installing PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install PostgreSQL OS packages either the same server as GovReady-Q or on a different database server.

.. code:: bash

   sudo apt install postgresql postgresql-contrib
   postgresql-setup initdb

Then set up the user and database (both named ``govready_q``):

.. code:: bash

   sudo -iu postgres createuser -P govready_q
   # Paste a long random password when prompted

   sudo -iu postgres createdb govready_q

Postgres’s default permissions automatically grant users access to a
database of the same name.

Make a note of the Postgres host, port, database name, user and password to add to GovReady-Q's configuration file at ``local/environment.json``.

.. code:: json

   {
      ...
      "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
      ...
   }

**Encrypting your connection to PostgreSQL running on a separate database server**

If PostgreSQL is running on a separate host, it is highly recommended you follow the below instructions
to configure a secure connection between GovReady-Q and PostgreSQL.

In ``/var/lib/pgsql/data/postgresql.conf``, enable TLS connections by
changing the ``ssl`` option to

.. code:: bash

   ssl = on 

and enable remote connections by binding to all interfaces:

.. code:: bash

   listen_addresses = '*'

Enable remote connections to the database *only* from the webapp server
and *only* encrypted with TLS by editing
``/var/lib/pgsql/data/pg_hba.conf`` and adding the line (replacing the
hostname with the hostname of the Q webapp server):

.. code:: bash

   hostssl all all webserver.example.com md5

Generate a self-signed certificate (replace ``db.govready-q.internal``
with the database server’s hostname if possible):

.. code:: bash

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

4. Installing GovReady-Q
------------------------

At this point, you have installed required OS packages, cloned the GovReady-Q repository and configured your preferred database option of SQLITE3, MySQL, or PostgreSQL.

Make sure you are in the base directory of the GovReady-Q repository.

Run the install script to install required Python libraries, initialize GovReady-Q's database and create a superuser. This is the same command for all database backends.

.. code:: bash

   # Run the install script to install Python libraries,
   # intialize database, and create Superuser
   ./install-govready-q
   
.. note::
   The command ``install-govready-q.sh`` creates the Superuser interactively allowing you to specify username and password.

   The command ``install-govready-q.sh --non-interactive`` creates the Superuser automatically for installs where you do
   not have access to interactive access to the commandline. The auto-generated username and password will be generated once to the standout log.


.. note::
   As of 0.9.1.20, the "govready-url" environment parameter is preferred way to set Django internal security, url,
   ALLOWED_HOST, and other settings instead of deprecated environment parameters "host" and "https".
   The "host" and "https" deprecated parameters will continue to be support for reasonable period for legacy installs.

   Deprecated (but supported for a reasonable period):

   .. code:: json

      {
         "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
         "host": "localhost:8000",
         "http": false,
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

5. Starting GovReady-Q
-----------------------

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


6. Stopping GovReady-Q
----------------------

Press ``CTL-c`` in the terminal window running GovReady-Q to stop the server. 

7. Additional options
---------------------

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

Instructions tested in May 2020 on Ubuntu 20.04 on a Digital Ocean droplet and on LTS (Focal Fossa) `Ubuntu focal-20200423 Docker image <https://hub.docker.com/_/ubuntu>`__.
