.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_sources_ubuntu:

Ubuntu from sources
===================

This guide describes how to install the GovReady-Q server for Ubuntu 16.04 or greater from source code.
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
provide full functionality. Execute the following commands as root:

.. code:: bash

   # Update package list
   apt-get update

   # Install dependencies
   DEBIAN_FRONTEND=noninteractive \
   apt-get install -y \
   unzip git curl jq \
   python3 python3-pip \
   python3-yaml \
   graphviz pandoc \
   language-pack-en-base language-pack-en

   # Upgrade pip to version 20.1+
   python3 -m pip install --upgrade pip

   # Optionally install supervisord for monitoring and restarting GovReady-q; and NGINX as a reverse proxy
   apt-get install -y supervisor nginx

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
   These steps assume you are installing into the ``/opt/`` directory as root.

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
   These steps assume you are installing into the ``/home/govready-q`` directory as user ``govready-q``.

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

* SQLite3
* MySQL
* PostgreSQL

GovReady-Q will automatically default to and use a SQLite3 database
if you do not specify a database connection string in ``local/environment.json``.



3 (option a). Installing SQLite3 (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no setup necessary to use SQLite3. GovReady-Q will automatically install a local SQLite3 database
``local/db.sqlite3`` by default if no ``db`` parameter is set in ``local/environment.json``.

.. note::
   All files in ``govready-q/local`` are git ignored so that you can safely pull git updates.


3 (option b). Installing MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install MySQL OS packages either on the same server as GovReady-Q or on a different database server.

.. code:: bash

   # Install of MySQL OS packages
   sudo apt-get install -y mysql-server mysql-client

.. code:: bash

   # If you intend to use optional configurations, such as the MySQL adapter, you
   # may need to run additional `pip3 install` commands, such as:
   pip3 install --user -r requirements_mysql.txt

Make a note of the MySQL's host, port, database name, user and password to add to GovReady-Q's configuration file at ``local/environment.json``.

.. code:: text

   {
      ...
      "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
      ...
   }

3 (option c). Installing PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install PostgreSQL OS packages either on the same server as GovReady-Q or on a different database server.

.. code:: bash

   sudo apt install -y postgresql postgresql-contrib
   postgresql-setup initdb

Then set up the user and database (both named ``govready_q``):

.. code:: bash

   sudo -iu postgres createuser -P govready_q
   # Paste a long random password when prompted

   sudo -iu postgres createdb govready_q

Postgres’s default permissions automatically grant users access to a
database of the same name.

Make a note of the Postgres host, port, database name, user and password to add to GovReady-Q's configuration file at ``local/environment.json``.

.. code:: text

   {
      ...
      "db": "postgres://USER:PASSWORD@HOST:PORT/NAME",
      ...
   }

**Encrypting your connection to PostgreSQL running on a separate database server**

If PostgreSQL is running on a separate host, it is highly recommended you follow the instructions below
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

Restart PostgreSQL:

.. code:: bash

   service postgresql restart

And if necessary, open the PostgreSQL port:

.. code:: bash

   firewall-cmd --zone=public --add-port=5432/tcp --permanent
   firewall-cmd --reload

4. Creating the local/environment.json file
-------------------------------------------

Create the ``local/environment.json`` file with appropriate parameters. (Order of the key-value pairs is not significant.)

**SQLite (default)**

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
   ALLOWED_HOST, and other settings, instead of the deprecated environment parameters "host" and "https".
   The deprecated "host" and "https" parameters will continue to be supported for a reasonable period for legacy installs.

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
   # initialize database, and create Superuser
   ./install-govready-q

.. note::
   The command ``install-govready-q.sh`` creates the Superuser interactively allowing you to specify username and password.

   The command ``install-govready-q.sh --non-interactive`` creates the Superuser automatically for installs where you do
   not have access to interactive access to the command line. The auto-generated username and password will be output (only once) to the stdout log.

6. Starting and stopping GovReady-Q
-----------------------------------

**Starting GovReady-Q**

You can now start GovReady-Q Server. GovReady-Q defaults to listening on localhost:8000, but can easily be run to listen on other host domains and ports.

.. code:: bash

   # Run the server on the default localhost and port 8000
   python3 manage.py runserver

Visit your GovReady-Q site in your web browser at: http://localhost:8000/

.. code:: bash

   # Run the server to listen at a different specific host and port
   # python manage.py runserver host:port
   python3 manage.py runserver 0.0.0.0:8000
   python3 manage.py runserver 10.0.167.168:8000
   python3 manage.py runserver example.com:8000

**Stopping GovReady-Q**

Press ``Ctrl-C`` in the terminal window running GovReady-Q to stop the server.

7. Running GovReady-Q with Gunicorn HTTP WSGI
---------------------------------------------

In this step, you will configure your deployment to use a higher performing, multi-threaded gunicorn (Green Unicorn) HTTP WSGI server
to handle web requests instead of GovReady-Q using Django's built-in server.
This will serve you pages faster, with greater scalability.
You will start gunicorn server using a configuration file.

First, create the ``local/gunicorn.conf.py`` file that tells gunicorn how to start.

.. code:: python

   import multiprocessing
   command = 'gunicorn'
   pythonpath = '/home/govready-q/govready-q'
   # serve GovReady-Q locally on server to use nginx as a reverse proxy
   bind = 'localhost:8000'
   workers = multiprocessing.cpu_count() * 2 + 1 # recommended for high-traffic sites
   # set workers to 1 for now, because the secret key won't be shared if it was auto-generated,
   # which causes the login session for users to drop as soon as they hit a different worker
   # workers = 1
   worker_class = 'gevent'
   user = 'govready-q'
   keepalive = 10

# start command
# gunicorn -c /home/govready-q/govready-q/gunicorn.config.py siteapp.wsgi


.. note::
   Alternatively set ``workers = 1`` if secret key is being auto-generated and not defined
   in local/environment.json. Auto-generated keys cause user login sessions to
   drop when their request is handled by a different worker.

.. note::
   A sample ``gunicorn.conf.py`` is provided in ``local-examples/local-centos-postgres-nginx-gunicorn-supervisor-http/gunicorn``.
   You can copy the contents of this file to ``local/gunicorn.conf.py``.

   .. code:: bash

      cp local-examples/local-centos-postgres-nginx-gunicorn-supervisor-http/gunicorn.conf.py \
      local/gunicorn.conf.py

**Starting GovReady-Q with Gunicorn**

You can now start Gunicorn web server from the GovReady-Q install directory. You can run the command to start
gunicorn as ``root`` or as the ``govready-q`` user.

.. code:: bash

   su - govready-q
   cd /home/govready-q/govready-q/
   gunicorn -c /home/govready-q/govready-q/local/gunicorn.conf.py siteapp.wsgi

   # Gunicorn is now running at serving GovReady-Q at the `govready-url` address.

**Stopping GovReady-Q with Gunicorn**

Press ``Ctrl-C`` in the terminal window running gunicorn to stop the server.


8. Monitoring GovReady-Q with Supervisor
----------------------------------------

In this step, you will configure your deployment to use Supervisor to start, monitor, and automatically restart Gunicorn (and GovReady-Q) as long running process. In this configuration Supervisord is the effective server daemon running in the background
and managing the gunicorn web server process handling requests to GovReady-Q. If Gunicorn or GovReady-Q unexpectedly crash, the Supervisord daemon will automatically restart Gunicorn and GovReady-Q.

Create the Supervisor ``/etc/supervisor/conf.d/supervisor-govready-q.conf`` conf file for gunicorn to run GovReady-Q.
Supervisor on Ubuntu automatically reads the configuration files in ``/etc/supervisor/conf.d/`` when started.

.. code:: ini

   [program:govready-q]
   command = gunicorn --config /home/govready-q/govready-q/local/gunicorn.conf.py siteapp.wsgi
   directory = /home/govready-q/govready-q
   stderr_logfile = /var/log/govready-q-stderr.log
   stdout_logfile = /var/log/govready-q-stdout.log

   [program:notificationemails]
   command = python3.6 manage.py send_notification_emails forever
   directory = /home/govready-q/govready-q
   stderr_logfile = /var/log/notificationemails-stderr.log
   stdout_logfile = /var/log/notificationemails-stdout.log

.. note::
   A sample ``supervisor-govready-q.conf`` is provided in ``local-examples/local-centos-postgres-nginx-gunicorn-supervisor-http``. You can copy the contents of this file to ``local/gunicorn.conf.py``.

   .. code:: bash

      cp local-examples/local-centos-postgres-nginx-gunicorn-supervisor-http/supervisor-govready-q.conf \
      /etc/supervisor/conf.d/supervisor-govready-q.conf

Supervisor will write its socket file to ``/run/supervisor`` and its log files to ``/var/log/supervisor/``.

.. note::
   Adjust delivery of Supervisor logs on Ubuntu in the Supervisor configuration file ``/etc/supervisor/supervisord.conf``.

**Starting GovReady-Q with Supervisor**

Use supervisor to start gunicorn and GovReady-Q.

.. code:: bash

   # Start supervisor as root
   service supervisor restart

**Stopping GovReady-Q with Supervisor**

Use Supervisor to stop GovReady-Q.

.. code:: bash

   # Stop supervisor as root
   service supervisor stop

9. Using NGINX as a reverse proxy
---------------------------------

.. warning::
   These instructions for NGINX are still a work in progress as of June 2, 2020.

In this step, you will configure your deployment to use NGINX as a reverse proxy in front of Gunicorn as an extra layer of performance and security.

.. code::
   web client <-> NGINX reverse proxy <-> gunicorn web server <-> GovReady-Q (Django)

First, adjust the ``local/environment.json`` file to serve GovReady at the domain that will end-users will see in the browser.
We will use ``example.com`` in the documentation. Replace ``example.com`` with your domain (or IP address).

.. code:: json

      {
         ...
         "govready-url": "http://example.com:8000",
         ...
      }

Next, create the NGINX conf ``/etc/nginx/sites-available/nginx-govready-q.conf`` file for GovReady-Q.

.. code::

   server {
      listen 8888;
      server_name example.com;
      access_log  /var/log/nginx/govready-q.log;

      location / {
         proxy_pass http://localhost:8000;
         proxy_set_header Host $host;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
   }

.. note::
   A sample ``nginx-govready-q.conf`` is provided in ``local-examples/local-centos-postgres-nginx-gunicorn-supervisor-http``. You can copy the contents of this file to ``/etc/nginx/sites-available/nginx-govready-q.conf``.

   .. code:: bash

      cp local-examples/local-centos-postgres-nginx-gunicorn-supervisor-http/nginx-govready-q.conf \
      /etc/nginx/sites-available/nginx-govready-q.conf


Create a soft link in ``/etc/nginx/sites-enabled/nginx-govready-q.conf`` to the config file in ``/etc/nginx/sites-available/nginx-govready-q.conf``.

.. code:: bash

   ln -s /etc/nginx/sites-available/nginx-govready-q.conf /etc/nginx/sites-enabled/nginx-govready-q.conf

Start NGINX.

.. code:: bash

   # Restart NGINX
   sudo /etc/init.d/nginx stop

   # Also
   # service nginx stop

.. note::
   NGINX will answer requests on ``http://example.com:8888`` and forward to gunicorn that is running on ``http://localhost:8000`` and gunicorn will pass to GovReady-Q via a unix socket. The ``govready-url`` domain name in ``local/envrionment.json`` must match the NGINX ``server_name`` in ``/etc/nginx/sites-available/nginx-govready-q.conf``.

Stop NGINX.

.. code:: bash

   # Restart NGINX
   sudo /etc/init.d/nginx start

   # Also
   # service nginx restart

Stopping NGINX only stops the reverse proxy. Use previously described Supervisor commands to stop and start gunicorn (and GovReady-Q).

10. Additional options
----------------------

Installing GovReady-Q Server command-by-command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For situations in which more granular control over the install process is required, use the commands below to install GovReady-Q.

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
   not have access to interactive access to the command line. The auto-generated username and password will be output (only once) to
   to the stdout log.

Enabling PDF export
~~~~~~~~~~~~~~~~~~~

To activate PDF and thumbnail generation, add ``gr-pdf-generator`` and
``gr-img-generator`` environment variables to your
``local/environment.json`` configuration file:

.. code:: text

   {
      ...
      "gr-pdf-generator": "wkhtmltopdf",
      "gr-img-generator": "wkhtmltopdf",
      ...
   }

Deployment utilities
~~~~~~~~~~~~~~~~~~~~

GovReady-Q can be optionally deployed with NGINX and Supervisor. There's also a script for updating GovReady-Q.

Sample ``nginx.conf``, ``supervisor.conf``, and ``update.sh`` files can
be found in the source code directory ``deployment/ubuntu``.

Notes
=====

Instructions tested in May 2020 on Ubuntu 20.04 on a Digital Ocean droplet and on LTS (Focal Fossa) `Ubuntu focal-20200423 Docker image <https://hub.docker.com/_/ubuntu>`__.
