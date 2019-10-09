# Deploying on Ubuntu

## Quickstart

.. container:: content-tabs

    .. tab-container:: ubuntu
        :title: Ubuntu 16.04

        .. rubric:: Installing on Ubuntu
        
        Instructions provide basic guidance on setting up GovReady-Q on an Ubuntu 16.04 server with Nginx. These commands should be run from the root directory of the GovReady-Q code repository.

        GovReady-Q calls requires Python 3.6 or higher to run and several Linux packages to provide full functionality.

        .. code-block:: bash

            # upgrade apt-get
            apt-get update && apt-get upgrade -y

            # install dependencies
            apt-get install -y \
              unzip \
              python3 python-virtualenvpython3-pip \
              python3-yaml \
              nginx uwsgi-plugin-python3supervisor \
              memcached \
              graphviz

            # optional install gcc to build the uWSGI Python package.
            sudo yum install gcc

            # optional insall of postgress and/or mysql
            apt-get install -y postgresql mysql-devel

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

## Additional Details

### Deployment utilities

Sample `apache.conf`, `superviser.ini`, and `update.sh` files can be found in the source code directory `deployment/ubuntu`.

### Creating a UNIX user named `govready-q`

You may find it useful to create a user specifically for GovReady-Q. Do this before installing GovReady-Q.

    # create user
    useradd govready-q -c "govready-q"

    # change permissions so that Apache can read static files.
    chmod a+rx /home/govready-q

    # change to govready-q user
    sudo su govready-q

### Installing drivers for Postgres, MySQL

    # if you intend to use optional configurations, such as the MySQL adapter, you
    # may need to run additional `pip3 install` commands, such as:
    # pip3 install --user -r requirements_mysql.txt

### local/environment.json

Configure GovReady-Q by creating a file in `local/environment.json` with the following content:

	{
	  "debug": false,
	  "admins": [["Name", "email@domain.com"], ...],
	  "host": "q.<yourdomain>.com",
	  "https": true,
	  "secret-key": "something random here",
	  "static": "/home/user/public_html"
	}

You can use [Django Secret Key Generator](https://www.miniwebtool.com/django-secret-key-generator/) to make a secret-key value.

Prepare static files:

	mkdir -p /home/user/public_html/static
	python3 manage.py collectstatic --noinput

Set up supervisor to run the uwsgi daemon:

	ln -sf `pwd`/deployment/ubuntu/supervisor.conf /etc/supervisor/conf.d/q.govready.com.conf
	service supervisor restart
