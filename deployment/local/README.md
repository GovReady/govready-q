Installing GovReady-Q Compliance Server on Workstations for Development
=======================================================================

1. [Installing with Docker](#docker)
1. [Installing source code on workstations to contribute](#development)
1. [Deployment guides](#deployment)


## <a name="docker"></a> Installing with Docker

The easiest way to get started with GovReady-Q is to launch Q through Docker.

See [Launching with Docker](../docker/README.md).


## <a name="development"></a> Installing source code on workstations to contribute

You can also install this repository on your workstation to contribute to improving GovReady-Q's functionality.

First, run the following commands to set up your local development environment:

	# install python3 and pip appropriately for your environment
	# below command demonstrates Ubuntu
	sudo apt-get install python3-pip unzip libssl-dev pandoc xvfb wkhtmltopdf # or appropriate for your system
	
	# clone repo
	git clone https://github.com/GovReady/govready-q
	
	# install dependencies
	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh
	
	# set up database (sqlite3 will be used until you configure another database)
	python3 manage.py migrate
	python3 manage.py load_modules

    # A default AppSource for https://github.com/GovReady/govready-sample-apps.
    python3 manage.py loaddata deployment/docker/appsources.json

Then create your admin account:

	python3 manage.py createsuperuser

And start the debug server:

	python3 manage.py runserver

On your first run, you'll be prompted to copy some JSON data into a file at `local/environment.json` like this:

    {
      "debug": true,
      "host": "localhost:8000",
      "https": false,
      "secret-key": "...something here..."
    }

This file is important for persisting login sessions, and you can provide other Q settings in this file.

## Create an organization

Q is designed for the enterprise, so all end-user interactions with Q are on segregated subdomains called "organizations". You must set up the first organization.

Visit [http://localhost:8000/](http://localhost:8000) and sign in with the superuser account that you created above. Then on the left side of the page, create your first organization:

![New Organization](assets/new_org.png)

Follow the instructions to visit your site's subdomain, e.g. at [http://my-first-organization.localhost:8000](http://my-first-organization.localhost:8000). We recommend using Google Chrome at this point. Other browsers will not be able to resolve organization subdomains on `localhost` unless you add `127.0.0.1 my-first-organization.localhost` [to your hosts file](https://support.rackspace.com/how-to/modify-your-hosts-file/).

When you log in for the first time it will ask you questions about the user and about the organization.

## Invitations on local systems

You will probably want to try the invite feature at some point. The debug server is configured to dump all outbound emails to the console. So if you "invite" others to join you within the application, you'll need to go to the console to get the invitation acceptance link.

## Updating the source code

To update the source code from this repository you can `git pull`. You then may need to re-run some of the setup commands:

	git pull
	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
