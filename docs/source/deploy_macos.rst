Deploying on macOS
==================

Quickstart
----------

.. container:: content-tabs

::

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
           # install wkhtmltopdf for generating PDFs, thumbnails
           # TAKE CAUTION WITH wkhtmltopdf security issues where crafted content renders server-side information
           brew cask install wkhtmltopdf

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

We welcome assistance with installing GovReady-Q natively on MacOS.
