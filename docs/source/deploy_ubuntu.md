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
		graphviz \
		libmysqlclient-dev

Configure nginx to use nginx.conf in this directory:

	# Turn off nginx's default website.
	rm -f /etc/nginx/sites-enabled/default

	# Put in our nginx site config.
	ln -sf `pwd`/deployment/ubuntu/nginx.conf /etc/nginx/sites-enabled/yourdomain.com

	service nginx restart

The nginx conf file assumes a certificate chain and private key are present at `/etc/ssl/local/ssl_certificate.crt/key`.

Install dependencies:

	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh

Configure GovReady-Q by creating a file in `local/environment.json` with the following content:

	{
	  "debug": false,
	  "admins": [["Name", "email@domain.com"], ...],
	  "host": "q.<yourdomain>.com",
	  "organization-parent-domain": "<yourdomain>.com",
	  "organization-seen-anonymously": false,
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

