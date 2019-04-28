Installing GovReady-Q for Development or Contributing
=======================================================================

This page provides instructions on how to install and run GovReady-Q in a mode suitable for making and testing changes to the software (i.e., in a Dev environment).

## Initial Prep & Installation

Begin by installing Q and its dependencies. This can be done either [on the host OS](deploy_host_os.html), or as a [Docker container](deploy_docker.html). For development purposes, installing on the host OS is currently the recommended approach.

When installing to the host OS, there are instructions for several operating systems, such as [yum-based Linux distributions](deploy_rhel7_centos7.html) and [apt-based Linux distributions](deploy_ubuntu.html). On other [Unix-based operating systems](deploy_generic_unix.html) (including macOS), GovReady-Q can generally be installed successfully, although some troubleshooting may be neccessary if we do not have instructions for your OS/distro. On Windows, only Docker containers are currently supported.

## Check Installation

Once GovReady-Q is installed, create your admin account and an initial organization, if you have not already done so:

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
	pip3 install --user -r requirements.txt
	./fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
