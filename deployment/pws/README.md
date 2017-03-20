# Deployment Scripts for Pivotal Web Services

This directory contains documentation and scripts for deployment to Pivotal Web Services (PWS) using Cloud Foundry tools.

# PWS Services

The PWS space should be configured with:

* Pivotal SSL
* New Relic
* User Provided: Papertrail
* ElephantSQL

# PWS Configuration

The Env Variables tab in PWS must be set with some application-specific data in the `ENVIRONMENT_JSON` field. We pass things into Django via JSON, which if you paste it into the field should lose its newlines to make a really long string (and that's good).

This needs to be done just the first time the app is created in PWS.

You can copy and modify from this, but _delete the comments_ before you paste it into the environment variable field because comments are actually not valid JSON:

	{
	  "debug": true, # Controls the Django DEBUG setting. Should be false in production.
	  "host": "q.govready.com", # domain of main landing site
	  "organization-parent-domain": "govready.com", # parent domain of organization subdomains
	  "admins": [ # List of people who get Django error emails.
	    ["name", "...@govready.com"]
	  ],
	  "secret-key": "....", # make a fresh string for new environments, see Django documentation
	  "email": {
	    "host": "smtp.mailgun.org",
	    "port": "587",
	    "user": "postmaster@mg.govready.com",
	    "pw": "...." # copy from Mailgun
	  },
	  "mailgun_api_key": "key-...", # copy from Mailgun (this is for incoming email)
	  "govready_cms_api_auth": ["...username...", "...password..."]
	}

# Other Configuration

You'll also need to configure Mailgun to send incoming replies to notification emails to an HTTP hook by giving Mailgun a URL on our domain hosted at PWS.

TODO: Add explanation of that.

# Performing a Deployment

To deploy to Pivotal Web Services, change to this directory and then run:

	./deploy.sh

This deploy script:

* Makes a fresh clone of the Q source code into `src`, cloning from your local checkout (`../../.git`).
* Installs and configures the Cloud Foundry command-line client (CLI), on first run.
* Fetches remote vendor resources that are required to build the app container.
* Pushes everything to the `GovReady` organization `dev` space as the app `govready-q`, first by creating a new app and, on success, swapping the old app and the new app and then killing the routes for the old app.

Note that a zero-downtime deployment like this should not be run if there are backwards-incompatible changes such as to the database schema, since there will be old and new code running concurrently while the deployment finishes.

# Continuous Integration

The `circle.yml` file is an example for using CircleCI to execute a deployment (as above) each time this repository is updated, or via a Rebuild on CircleCI. CircleCI should be set up with the environment variables `PWS_USER` and `PWS_PASS` that hold the credentials for Pivotal Web Services.

See the `circle.yml` in this repository's root for the actual CircleCI configuration file.

# Notes

To tinker around with Python interactively on a running PWS container:

	cf ssh govready-q

	# fix somehow incorrect environment
	HOME=~/app/ . ~/app/.profile.d/python.sh 

	python -V # should be 3.5.3!

