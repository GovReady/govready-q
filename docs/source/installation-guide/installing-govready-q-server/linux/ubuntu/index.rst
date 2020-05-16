.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_sources_ubuntu:

Ubuntu from sources
===================

This guide describes how to install the GovReady-Q server for Ubuntu 20.04 or greater from source code.


.. note::
    Instructions applicable for Ubuntu 20.04 LTS (Focal Fossa)
    Tested on an `Ubuntu focal-20200423 Docker image <https://hub.docker.com/_/ubuntu>`__.

Installing required OS packages
-------------------------------

GovReady-Q requires Python 3.6 or higher and several Linux packages to
provide full functionality. Execute the following commands:

.. code:: bash

   # Update package list
   sudo apt-get update

   # Install dependencies
   DEBIAN_FRONTEND=noninteractive \
       sudo -E apt-get install \
       unzip git curl \
       python3 python3-pip \
       python3-yaml \
       graphviz pandoc \
       language-pack-en-base language-pack-en

   # To optionally generate thumbnails and PDFs for export, you must install wkhtmltopdf
   # WARNING: wkhtmltopdf can expose you to security risks. For more information,
   # search the web for "wkhtmltopdf Server-Side Request Forgery"
   read -p "Are you sure (yes/no)? " ; if [ "$REPLY" = "yes" ]; then sudo apt-get install wkhtmltopdf ; fi

Installing desired database
---------------------------

GovReady-Q requires a relational database. You can choose:

* SQLITE3 (default)
* MySQL
* PostgreSQL

Installing SQLITE3 (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GovReady-Q will automatically install a local SQLITE3 database by default.

The SQLITE3 file will be installed within the GovReady-Q directory structure as
``local/db.sqlite3``.

.. note::
   SQLITE3 is not recommended for production. SQLITE3 database -- AND YOUR DATA -- will be destroyed when you delete the virtual machine (or container) running GovReady-Q.

Installing MySQL (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the database server, install PostgreSQL OS packages:

.. code:: bash

   # Install of MySQL OS packages
   sudo apt-get install mysql-server mysql-client

   # Install of MySQL Python libraries
   pip3 install --user -r requirements_mysql.txt

.. note::
   MySQL can be installed locally on the same host as GovReady-Q or on a separate host.
   
   Your MySQL database -- AND YOUR DATA -- will be destroyed on same-host installs when you delete the virtual machine (or container) running GovReady-Q.


Installing PostgreSQL (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the database server, install PostgreSQL OS packages:

::

   sudo apt install postgresql postgresql-contrib
   postgresql-setup initdb

.. note::
   PostgreSQL can be installed locally on the same host as GovReady-Q or on a separate host.
   
   Your PostgreSQL database -- AND YOUR DATA -- will be destroyed on same-host installs when you delete the virtual machine (or container) running GovReady-Q.

Then set up the user and database (both named ``govready_q``):

::

   sudo -iu postgres createuser -P govready_q
   # Paste a long random password when prompted

   sudo -iu postgres createdb govready_q

Postgres’s default permissions automatically grant users access to a
database of the same name.

**Optional PostgreSQL TLS connection**

.. note::
   If PostgreSQL is running on a separate host, it is highly recommended you configure a secure connection between GovReady-Q and PostgreSQL.

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

   hostssl all all webserver.hostname.com md5

Generate a self-signed certificate (replace ``db.govready-q.internal``
with the database server’s hostname if possible):

::

   openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /var/lib/pgsql/data/server.key -out /var/lib/pgsql/data/server.crt -subj '/CN=db.govready-q.internal'
   chmod 600 /var/lib/pgsql/data/server.{key,crt}
   chown postgres.postgres /var/lib/pgsql/data/server.{key,crt}

Copy the certificate to the webapp server so that the webapp server can
make trusted connections to the database server:

::

   cat /var/lib/pgsql/data/server.crt
   # Place on webapp server at /home/govready-q/pgsql.crt

Then restart the database:

::

   service postgresql restart

And if necessary, open the Postgres port:

::

   firewall-cmd --zone=public --add-port=5432/tcp --permanent
   firewall-cmd --reload


Installing GovReady-Q
---------------------

.. note::
   You may find it useful to create a Linux user specifically for GovReady-Q. Do
   this before installing GovReady-Q.

   .. code:: bash

      # Create user
      useradd govready-q -m -c "govready-q"

      # Change permissions so that the webserver can read static files
      chmod a+rx /home/govready-q

      # Switch to the govready-q user
      su govready-q

Clone the GovReady source code and install packages.

.. code:: bash

   # Clone GovReady-Q
   git clone https://github.com/govready/govready-q
   cd govready-q

   # Cnstall Python 3 packages
   pip3 install --user -r requirements.txt

   # Install Bootstrap and other vendor resources locally
   ./fetch-vendor-resources.sh

If you are using MySQL or PostgreSQL, you must specify the database connection string in GovReady-Q's configuration file at ``local/environment.json``.
(SQLITE3 does not need to be specified.) Enter your database credentials for the ``db`` connection string.

**MySQL**

.. code:: json

   {
     "db": "mysql://USER:PASSWORD@HOST:PORT/NAME",
     "debug": false,
     "host": "localhost:8000",
     "https": false,
     "secret-key": "...something here..."
   }

**PostgreSQL**

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

**Initialize the GovReady-Q database**

Run the final setup commands to initialize GovReady-Q's database.
This is the same command regardless of which backend database being used.

.. code:: bash

   # Run database migrations (sqlite3 database used by default)
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
   A Superuser and Organization needs to be created as part of initialization. The Superuser provides
   access to the GovReady-Q Django Admin interface to configure compliance questionnaires and other admin settings.

   The command ``python3 manage.py first_run`` creates the Superuser interactively allowing you to specify username and password.

   The command ``python3 manage.py first_run --non-interactive`` creates the Superuser automatically for installs where you do
   not have access to interactive access to the commandline. The auto-generated username and password will be generated once to
   to the standout log.

   Finally, it is possible to create a Superadmin account via the Django shell interface.

Starting GovReady-Q
-------------------

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

(Optional) Enabling PDF export
------------------------------

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

(Optional) Deployment utilities
-------------------------------

Sample ``nginx.conf``, ``supervisor.confg``, and ``update.sh`` files can
be found in the source code directory ``deployment/ubuntu``.

