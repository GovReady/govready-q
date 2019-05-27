# Deploying on macOS

## Quickstart

.. container:: content-tabs

    .. tab-container:: macos
        :title: macOS

        .. rubric:: Installing on macOS
        
        GovReady-Q calls requires Python 3.6 or higher to run and several Linux packages to provide full functionality.

        .. code-block:: bash

            # install dependencies using brew
            brew install python3
            # other packages: unzip, graphviz, pandoc,
            # xorg-x11-server-Xvfb wkhtmltopdf \

            # optional install gcc to build the uWSGI Python package.
            # Needed on macOS?

            # optional insall of postgress and/or mysql
            # brew install instructions

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
            python3 manage.py migrate

        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/

## Additional Details

We welcome assistance with installing GovReady-Q natively on MacOS.
