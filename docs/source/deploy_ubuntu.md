# Deploying GovReady-Q to Ubuntu Linux

This document provides some basic guidance on setting up GovReady-Q on an Ubuntu 16.04 server with Nginx. These commands should be run from the root directory of the GovReady-Q code repository.

Update system packages and install packages helpful for GovReady-Q:

	apt-get update && apt-get upgrade -y

	apt-get install -y \
		unzip \
		python3 python-virtualenv python3-pip \
		python3-yaml \
		nginx uwsgi-plugin-python3 supervisor \
		memcached \
		graphviz

Install dependencies:

	pip3 install --user -r requirements.txt
	./fetch-vendor-resources.sh

Configure GovReady-Q by creating a file in `local/environment.json` with the following content:

	{
	  "debug": false,
	  "admins": [["Name", "email@domain.com"], ...],
	  "host": "q.<yourdomain>.com",
	  "https": true,
	  "secret-key": "something random here",
	  "static": "/home/user/public_html"
	}

You can use [Django Secret Key Generator](https://www.miniwebtool.com/django-secret-key-generator/) to make a secret-key value.

Prepare the database:

	python3 manage.py migrate
	python3 manage.py createsuperuser

Prepare static files:

	mkdir -p /home/user/public_html/static
	python3 manage.py collectstatic --noinput

Set up supervisor to run the uwsgi daemon:

	ln -sf `pwd`/deployment/ubuntu/supervisor.conf /etc/supervisor/conf.d/q.govready.com.conf
	service supervisor restart

## Next steps (Production or Development configuration)

If you're deploying GovReady-Q to a production environment, see the [Production deployment steps](deploy_prod.html).

If you're deploying GovReady-Q for development or evaluation purposes, [Development deployment steps](deploy_local_dev.html) may be useful for you.
