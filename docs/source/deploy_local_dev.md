# Deploying GovReady-Q for Development

This page provides additional tips for installing and run GovReady-Q in a mode suitable for making and testing changes to the software (i.e., in a Dev environment).

## Quickstart

For local development, there is a quickstart script available to speed up environment setup. After installing system requirements through your package manager, run the following 3 commands in order to set up GovReady-Q in a new directory:

```
git clone https://github.com/govready/govready-q
cd govready-q
./first_run.sh
```

This will set up a `local/environment.json` file suitable for a dev environment; set up local dependencies; and run the assorted initial manage.py commands (`migrate`, `load_modules`, `first_run`, etc.). Additionally, it can run common post-installation steps, based on user input.

The `first_run.sh` script is set up to take user input, and is expected to be run interactively.

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
