.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_sources_centos_rhel:

CentOS / RHEL 7 from sources
============================

This guide describes how to install the GovReady-Q server for CentOS 7 or greater from source code.


.. note::
    Instructions applicable for RHEL 7 and CentOS 7.
    Tested on a `CentOS 7.8.2003 Docker image <https://hub.docker.com/_/centos>`__.

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
   unzip git2u jq nmap-ncat \
   graphviz pandoc

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

Clone the GovReady-Q repository from GitHub into the desired directory on your CentOS server.

.. code:: bash

   # Clone GovReady-Q
   git clone https://github.com/govready/govready-q
   cd govready-q

.. note::
   You may find it useful to create a Linux user specifically for GovReady-Q before cloning GovReady-Q.

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

3. Installing desired database
------------------------------

GovReady-Q requires a relational database. You can choose:

* SQLITE3 (default)
* MySQL
* PostgreSQL

3 (option a). Installing SQLITE3 (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GovReady-Q will automatically install a local SQLITE3 database by default.

The SQLITE3 file will be installed within the GovReady-Q directory structure as
``local/db.sqlite3``.

.. warning::
   SQLITE3 is not recommended for production. SQLITE3 database -- AND YOUR DATA -- will be destroyed when you delete the virtual machine (or container) running GovReady-Q.

3 (option b). Installing MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the database server, install MySQL OS packages:

.. code:: bash

   # Install of MySQL OS packages
    sudo yum install mysql-devel

You must specify the database connection string in GovReady-Q's configuration file at ``local/environment.json``.

.. code:: json

   {
   "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
   "debug": false,
   "host": "localhost:8000",
   "https": false,
   "secret-key": "...something here..."
   }

.. note::
   See `Environment Settings <Environment.html>`__ for a complete list of configuration options.

.. warning::
   MySQL can be installed locally on the same host as GovReady-Q or on a separate host.
   Your MySQL database -- AND YOUR DATA -- will be destroyed on same-host installs when you delete the virtual machine (or container) running GovReady-Q.


3 (option c). Installing PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the database server, install PostgreSQL OS packages:

.. code:: bash

   sudo yum install postgresql mysql-devel
   # postgresql-setup initdb

Then set up the user and database (both named ``govready_q``):

.. code:: bash

   sudo -iu postgres createuser -P govready_q
   # Paste a long random password when prompted

   sudo -iu postgres createdb govready_q

Postgres’s default permissions automatically grant users access to a
database of the same name.

You must specify the database connection string in GovReady-Q's configuration file at ``local/environment.json``.

.. code:: json

   {
   "db": "postgres://USER:PASSWORD@HOST/DATABASE",
   "debug": false,
   "host": "localhost:8000",
   "https": false,
   "secret-key": "...something here..."
   }

.. note::
   See `Environment Settings <Environment.html>`__ for a complete list of configuration options.

.. warning::
   PostgreSQL can be installed locally on the same host as GovReady-Q or on a separate host.
   Your PostgreSQL database -- AND YOUR DATA -- will be destroyed on same-host installs when you delete the virtual machine (or container) running GovReady-Q.

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


5. Starting GovReady-Q
-----------------------

.. code:: bash

   # Run the server
   python3 manage.py runserver

Visit your GovReady-Q site in your web browser at:

http://localhost:8000/


It is not necessary to specify a port. GovReady-Q will read the ``local/environment.json`` file to determine
host name and port.

.. code:: bash

   # Run the server
   python3 manage.py runserver

.. note::
    Depending on host configuration both ``python3`` and ``python`` commands will work.

    GovReady-Q can run on ports other than ``8000``. Port ``8000`` is selected for convenience.

    GovReady-Q defaults to `localhost:8000` when launched with ``python manage.py runserver``.


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
