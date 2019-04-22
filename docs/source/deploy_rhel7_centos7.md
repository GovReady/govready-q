# Deploying Q to Red Hat Enterprise Linux 7 / CentOS 7 / Amazon Linux 2

<!-- Please update the project's Vagrantfile when revising these instructions. -->

These instructions can be used to configure a Red Hat Enterprise Linux 7, CentOS 7, or Amazon Linux 2 system to run GovReady-Q.
A Vagrantfile based on CentOS 7 and these instructions is also provided at the root of the GovReady-Q source code.

## Preparing System Packages

GovReady-Q calls out to `git` to fetch apps from git repositories, but that requires git version 2 or later because of the use of the GIT_SSH_COMMAND environment variable. RHEL stock git is version 1. Switch it to version 2+ by using the IUS package:

    # if necessary, enable EPEL and IUS repositories
    rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm https://rhel7.iuscommunity.org/ius-release.rpm

    # if necessary, remove any git currently installed
    yum remove git

    yum install git2u

## Preparing Q Source Code

Create a UNIX user named `govready-q`:

    # Create user.
    useradd govready-q -c "govready-q"
    
    # Change permissions so that Apache can read static files.
    chmod a+rx /home/govready-q

Deploy GovReady-Q source code:

    # Install required software.
    #
    # Note that python34-devel and mysql-devel are needed to compile & install
    # the mysqlclient Python package. But mysql-devl has an installation conflict
    # with IUS. Adding --disablerepo=ius fixes it.
    #
    # gcc is needed to build the uWSGI Python package.
    sudo yum install --disablerepo=ius \
        unzip gcc python34-pip python34-devel \
        graphviz \
        pandoc xorg-x11-server-Xvfb wkhtmltopdf \
        postgresql mysql-devel

Upgrade `pip` because the RHEL package version is out of date (we need >=9.1 to properly process hashes in `requirements.txt`):

    pip3 install --upgrade pip

Then switch to the govready-q user and install Q:

    sudo su govready-q
    cd
    git clone https://github.com/govready/govready-q
    cd govready-q
    git checkout {choose the tag for the current released version}
    pip3 install --user -r requirements.txt
    ./fetch-vendor-resources.sh

    # if you intend to use optional configurations, such as the MySQL adapter, you
    # may need to run additional `pip3 install` commands, such as:
    # pip3 install -r requirements_mysql.txt
    
### Test Q with a Local Database

Run the final setup commands to initialize a local Sqlite3 database in `local/db.sqlite` to make sure everything is OK so far:

    python3 manage.py migrate
    python3 manage.py load_modules
    python3 manage.py createsuperuser

And test that the site starts in debug mode at localhost:8000:

	python3 manage.py runserver

### Set basic configuration variables

Create a file named `local/environment.json` (ensure it is not world-readable) that contains site configuration in JSON:

	{
	  "debug": false,
	  "host": "webserver.hostname.com",
	  "organization-parent-domain": "webserver.hostname.com",
	  "https": true,
	  "secret-key": "generate random string using e.g. https://www.miniwebtool.com/django-secret-key-generator/",
	  "static": "/home/govready-q/public_html/static"
	}

Because of host header checking, to test the site again using `python3 manage.py runserver` you will need to visit it using `webserver.hostname.com` and not `localhost`. (Be sure to replace `webserver.hostname.com` with your hostname.)

## Setting up the Database Server

For production deployment, it is recommended to use dedicated database software, rather than SQLite.

The recommended database is PostgreSQL - see [instructions on setting up Q with PostgreSQL](configure_db.html)

## Setting up a Webserver

It's recommended to run a dedicated webserver software, such as Apache or Nginx, as a reverse proxy in front of the Q application (running through uWSGI). To read how to do this, see [instructions on setting up Q with a reverse proxy webserver](configure_webserver.html).

## Creating the First User

If you are setting up a multi-tenant instance of Q where different organizations will use the site on different subdomains, create the administrative user using:

    python3 manage.py createsuperuser

and then log into the admin to create initial organizations.

Otherwise, for a single-tenant setup, add to `local/environment.json`:

  "single-organization": "main",

which will serve just the Organization instance whose subdomain field is "main", and then create the initial user and the "main" organization using:

	python3 manage.py first_run

You should now be able to log into GovReady-Q using the user created in this section.

## Setting up an HTTPS Certificate

The instructions above created a self-signed certificate to get the website up and running. To use Let's Encrypt to automatically provision a real certificate, install and run `certbot`:

	yum install -y python-certbot-apache
	certbot --apache -d webserver.hostname.com
	# and follow the prompts

Then set it to automatically renew certificates as needed:

	# edit root's crontab
	crontab -e

	# insert at end:
	30 2 * * * /usr/bin/certbot renew >> /var/log/le-renew.log

## Other Configuration Settings

Set up email by adding to `local/environment.json`:

	  "admins": [["Your Name", "you@company.com"]],
	  "email": {
	    "host": "smtp.server.com", "port": "587", "user": "...", "pw": "....",
	    "domain": "webserver.hostname.com"
	  },
	  "mailgun_api_key": "...",

## Updating Deployment

When there are changes to the GovReady-Q software, pull new sources and restart processes with:

    sudo -iu govready-q /home/govready-q/govready-q/deployment/rhel/update.sh
    
As root, you can also restart just the Python/Django process:    

    sudo supervisorctl restart all
    
But this won't do a full update so don't normally do that (it won't restart the separate notifications process or generate static assets, etc.).
