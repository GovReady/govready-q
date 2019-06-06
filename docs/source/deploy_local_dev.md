# Deploying GovReady-Q for Development

This page provides additional tips for installing and run GovReady-Q in a mode suitable for making and testing changes to the software (i.e., in a Dev environment).

## Creating local/environment.json file

When you first run GovReady-Q with `python manage.py runserver`, you'll be prompted to copy some JSON data into a file at `local/environment.json` like this:

    {
      "debug": true,
      "host": "localhost:8000",
      "https": false,
      "secret-key": "...something here..."
    }

This file is important for persisting login sessions, and you can provide other Q settings in this file.

## Invitations on local systems

You will probably want to try the invite feature at some point. The debug server is configured to dump all outbound emails to the console. So if you "invite" others to join you within the application, you'll need to go to the console to get the invitation acceptance link.

## Updating the source code

To update the source code from this repository you can `git pull`. You then may need to re-run some of the setup commands:

	git pull
	pip3 install --user -r requirements.txt
	./fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
