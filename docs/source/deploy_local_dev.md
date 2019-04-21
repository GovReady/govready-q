Installing GovReady-Q Compliance Server on Workstations for Development
=======================================================================

## Installing with Docker

The easiest way to get started with GovReady-Q is to launch Q through Docker.

See [Deploying GovReady-Q with Docker](deploy_docker.md).


## Installing source code on workstations to contribute

You can also install this repository on your workstation to contribute to improving GovReady-Q's functionality.

First, run the following commands to set up your local development environment:

	# Install Python 3, pip, and other system packages appropriately for your
	# environment. The commands below demonstrate how to do this on Ubuntu 16.04:
	sudo apt-get install python3-pip unzip pandoc xvfb wkhtmltopdf
	
	# Clone this repository.
	git clone https://github.com/GovReady/govready-q
	cd govready-q
	
	# Install dependencies.
	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh

	# if you intend to use optional configurations, such as the MySQL adapter, you
	# may need to run additional `pip3 install` commands, such as:
	# pip3 install -r requirements_mysql.txt
	
	# Set up the database (sqlite3 will be used until you configure another database).
	python3 manage.py migrate
	python3 manage.py load_modules

Then create your admin account and an initial organization:

	python3 manage.py first_run

	Let's create your first Q user. This user will have superuser privileges in the Q administrative interface.
	Username: admin
	Email address: you@example.com
	Password: *********
	Password (again): *********
	Superuser created successfully.
	Let's create your Q organization.
	Organization Name: The Secure Company

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

Visit [http://localhost:8000/admin](http://localhost:8000/admin) and sign in with the administrative account that you created above. Then on the left side of the page, click Organizations. An organization named `main` will be shown (it was created by the `first_run` script above).

Each organization is accessed on its own subdomain. The `main` organization will be at `http://main.localhost:8000`. We recommend using Google Chrome at this point. Other browsers will not be able to resolve organization subdomains on `localhost` unless you add a hostname record [to your hosts file](https://support.rackspace.com/how-to/modify-your-hosts-file/), e.g. `127.0.0.1 main.localhost`. If you want to change the subdomain, do so now. Then click Save and Continue Editing at the bottom of the page.

Click View On Site at the top of the page to go to the organization's landing page at http://main.localhost:8000. Then log in with your credentials again.

## Invitations on local systems

You will probably want to try the invite feature at some point. The debug server is configured to dump all outbound emails to the console. So if you "invite" others to join you within the application, you'll need to go to the console to get the invitation acceptance link.

## Updating the source code

To update the source code from this repository you can `git pull`. You then may need to re-run some of the setup commands:

	git pull
	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
