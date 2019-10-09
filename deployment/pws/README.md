# Deployment Scripts for Pivotal Web Services

**DEPRECATED APRIL 2018 - SEE READ THE DOCS VERSION**

This directory contains documentation and scripts for deployment to Pivotal Web Services (PWS) using Cloud Foundry tools.

## Create a PWS Space

A PWS "space" must be created manually.

The PWS space should be configured with the services:

* New Relic
* User Provided: Papertrail
* ElephantSQL

An app within the space must be configured manually as well --- see the next section.

## PWS App Configuration

### App Name

An app within the space must be configured manually before automated deployment will work, since automated deployment takes an existing app and clones its settings.

The app's name must be `govready-q-` followed by the name of the space. Ex: `govready-q-sandbox` if the space is named `sandbox`. (This rule is hard coded in `deploy.sh`. To avoid name clashes during blue-green deployments, the app name must be globally unique.)

### App Routes

Routes map public URLs to the app. You must create two routes:

* One route defines the Q landing page, which holds the Django admin.

* The second route defines organization subdomains.

When creating routes under domains we own (e.g. govready.com), the two routes should be of the form:

	sandbox.govready.com  <-- Q landing page
	*.sandbox.govready.com  <-- organization subdomains

Then the settings for the environment variable will be:

	"host": "sandbox.govready.com"

(Note: We haven't yet figured out how to do HTTPS when using our own domains on PWS.)

But when creating routes under one of PWS's domains so that it generates an https certificate for us, the routes should be:

	q-sandbox-admin.cfapps.io <-- Q landing page
	q-sandbox.cfapps.io <-- single organization subdomain (for org "q-sandbox")
	(create more organization subdomain routes if needed)

And the settings for the environment variable will be:

	"host": "q-sandbox-admin.cfapps.io"

(Although `sandbox` appears in the route here, the routes can be anything so long as the environment variables settings are adjusted accordingly.)

### App Environment Variables

The Env Variables tab in PWS must be set with some application-specific data in the `ENVIRONMENT_JSON` field. We pass things into Django via JSON, which if you paste it into the field should lose its newlines to make a really long string (and that's good).

This needs to be done just the first time the app is created in PWS.

You can copy and modify from this, but _delete the comments_ before you paste it into the environment variable field because comments are actually not valid JSON:

	{
	  "debug": true, # Controls the Django DEBUG setting. Should be false in production.
	  "host": "q.govready.com", # domain of main landing site
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

The `DISABLE_COLLECTSTATIC` variable must also be set to `1`, but this is set as a part of deployment. See `manifest-template.yaml`.

## Other Configuration

You'll also need to configure Mailgun to send incoming replies to notification emails to an HTTP hook by giving Mailgun a URL on our domain hosted at PWS.

TODO: Add explanation of that.

## Performing a Deployment

Before performing an automated deployment, you must set up a space and app manually. See above.

Choose which space you want to deploy to and authenticate with PWS:

	PWS_SPACE=sandbox
	cf api https://api.run.pivotal.io
	cf login

To deploy to Pivotal Web Services, change to this directory and then run:

	./deploy.sh

This deploy script:

* Makes a fresh clone of the Q source code into `src`, cloning from your local checkout (`../../.git`).
* Installs and configures the Cloud Foundry command-line client (CLI), on first run.
* Fetches remote vendor resources that are required to build the app container.
* Pushes everything to the `GovReady` organization `$PWS_SPACE` space as the app `govready-q-`$PWS_SPACE`, first by creating a new app and, on success, swapping the old app and the new app and then killing the routes for the old app.

Note that a zero-downtime deployment like this should not be run if there are backwards-incompatible changes such as to the database schema, since there will be old and new code running concurrently while the deployment finishes.

## Continuous Integration

The `circle.yml` file is an example for using CircleCI to execute a deployment (as above) each time this repository is updated, or via a Rebuild on CircleCI. CircleCI should be set up with the environment variables `PWS_USER` and `PWS_PASS` that hold the credentials for Pivotal Web Services.

See the `circle.yml` in this repository's root for the actual CircleCI configuration file.

## Notes

To tinker around with Python interactively on a running PWS container, such as to create the first Django admin user:

	cf ssh govready-q-${PWS_SPACE}

	# fix somehow incorrect environment
	HOME=~/app/ . ~/app/.profile.d/python.sh 

	python -V # should be 3.5.3!

	cd app/src

	# Create a superuser.
	./manage.py createsuperuser

	# After setting up module sources in the Django admin, you
	# may also want to log in and run load_modules. You could
	# also just restart the app from the PWS console since
	# load_modules is run on app startup.
	./manage.py load_modules
