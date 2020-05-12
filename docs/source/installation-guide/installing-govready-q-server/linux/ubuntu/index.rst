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

   # update package list
   sudo apt-get update

   # install dependencies
   DEBIAN_FRONTEND=noninteractive \
       sudo -E apt-get install \
       unzip git curl \
       python3 python3-pip \
       python3-yaml \
       graphviz pandoc \
       language-pack-en-base language-pack-en

   # to generate thumbnails and PDFs for export, you must install wkhtmltopdf
   # WARNING: wkhtmltopdf can expose you to security risks. For more information,
   # search the web for "wkhtmltopdf Server-Side Request Forgery"
   read -p "Are you sure (yes/no)? " ; if [ "$REPLY" = "yes" ]; then sudo apt-get install wkhtmltopdf ; fi

Installing GovReady-Q
~~~~~~~~~~~~~~~~~~~~~

Clone the GovReady source code and install packages.

.. code:: bash

   # clone GovReady-Q
   git clone https://github.com/govready/govready-q
   cd govready-q

   # install Python 3 packages
   pip3 install --user -r requirements.txt

   # install Bootstrap and other vendor resources locally
   ./fetch-vendor-resources.sh

Setting up GovReady-Q
~~~~~~~~~~~~~~~~~~~~~

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

Starting GovReady-Q
~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # run the server
   python3 manage.py runserver 0.0.0.0:8000

Visit your GovReady-Q site in your web browser at:

http://localhost:8000/


It is not necessary to specify a port. GovReady-Q will read the `local/enviroment.json` file to determine
host name and port.

.. code:: bash

   # run the server
   python3 manage.py runserver

.. note::
    Depending on host configuration both ``python3`` and ``python`` commands will work.

    GovReady-Q can run on ports other than ``8000``. Port ``8000`` is selected for convenience.

    GovReady-Q defaults to `localhost:8000` when launched with ``python manage.py runserver``.

    Tested on an `Ubuntu focal-20200423 Docker image <https://hub.docker.com/_/ubuntu>`__.


(Optional) Installing Postgres, MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GovReady-Q can optionally be configured to work with Postgress or MySQL database engines instead of the default SQLITE3.

.. code:: bash

   # optional install of postgres and/or mysql
   sudo apt-get install postgresql mysql-server mysql-client

.. code:: bash

   # if you intend to use optional configurations, such as the MySQL adapter, you
   # may need to run additional `pip3 install` commands, such as:
   pip3 install --user -r requirements_mysql.txt

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

(Optional) Enabling PDF export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To activate PDF and thumbnail generation, add ``gr-pdf-generator`` and
``gr-img-generator`` environment variables to your
``local/environment.json`` configuration file:

::

   {
      ...
      "gr-pdf-generator": "wkhtmltopdf",
      "gr-img-generator": "wkhtmltopdf",
      ...
   }

(Optional) Deployment utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sample ``nginx.conf``, ``supervisor.confg``, and ``update.sh`` files can
be found in the source code directory ``deployment/ubuntu``.

(Optional) Creating a dedicated GovReady UNIX user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may find it useful to create a user specifically for GovReady-Q. Do
this before installing GovReady-Q.

.. code:: bash

   # Create user.
   useradd govready-q -m -c "govready-q"

   # Change permissions so that the webserver can read static files.
   chmod a+rx /home/govready-q
