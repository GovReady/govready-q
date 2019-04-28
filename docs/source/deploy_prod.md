# Deploying GovReady-Q in Production environments

These instructions assume that GovReady-Q is installed by the user `govready-q`, in the directory `/home/govready-q/govready-q/`.

To verify that this is the case, run the following command, and check whether GovReady-Q responds to HTTP requests (on `localhost:8000` by default).

	cd /home/govready-q/govready-q/ && python3 manage.py runserver

If GovReady-Q is installed successfully, proceed with the rest of these configuration instructions. If it doesn't, see [OS-specific install instructions](deploy_host_os.html).

## Set basic configuration variables

Create a file named `local/environment.json` (ensure it is not world-readable) that contains site configuration in JSON, with some recommended settings:

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

    # replace $DISTRO with an appropriate value.
    # Currently-supported options include "rhel" and "ubuntu"
    sudo -iu govready-q /home/govready-q/govready-q/deployment/$DISTRO/update.sh
    
As root, you can also restart just the Python/Django process:    

    sudo supervisorctl restart all
    
But this won't do a full update so don't normally do that (it won't restart the separate notifications process or generate static assets, etc.).
