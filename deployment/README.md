Deployment
==========

Deployment guides for installing and deploying GovReady-Q on different Operating Systems can be found the `deployment` directory.

* [Launching with Docker](docker/README.md) - super easy and has a nice `first_run.sh` script
* [Installing on RHEL](rhel/README.md) - detailed instructions on installing, libraries, setting up Postgres and Apache
* [Installing on Ubuntu](ubuntu/README.md) - super easy `update.sh`

A production system may need to set more options in `local/environment.json`. Here are recommended settings:

	{
	  "debug": false,
	  "admins": [["Name", "email@domain.com"], ...],
	  "host": "q.<yourdomain>.com",
	  "organization-parent-domain": "<yourdomain>.com",
	  "organization-seen-anonymously": false,
	  "https": true,
	  "secret-key": "something random here",
	  "static": "/root/public_html"
	}
