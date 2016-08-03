#!/bin/bash

# On a new machine, run:
# sudo deployment/setup.sh

#########################################

DOMAIN=q.govready.com

# THE SYSTEM
############

# Update system packages.
apt-get update && apt-get upgrade -y

# Get nginx from a PPA to get version 1.6 so we can support HTTP/2	.
if [ ! -f /etc/apt/sources.list.d/nginx-stable-trusty.list ]; then
	sudo apt-get install -y software-properties-common # provides apt-add-repository
	sudo add-apt-repository -y ppa:nginx/stable
	sudo apt-get update
fi

# Install packages.
apt-get install -y \
	unzip \
	python3 python-virtualenv python3-pip \
	python3-yaml \
	nginx uwsgi-plugin-python3 supervisor \
	memcached

# Turn off nginx's default website.
rm -f /etc/nginx/sites-enabled/default

# Put in our nginx site config.
ln -sf `pwd`/deployment/nginx.conf /etc/nginx/sites-enabled/$DOMAIN

# Create a new TLS private key if we don't have one yet.
if [ ! -f /etc/ssl/local/ssl_certificate.key ]; then
	# Set the umask so the key file is never world-readable.
	(umask 077;
		openssl genrsa -out /etc/ssl/local/ssl_certificate.key 2048)
fi

# Generate a self-signed SSL certificate so that nginx can start.
if [ ! -f /etc/ssl/local/ssl_certificate.pem ]; then
	# Generate a certificate signing request.
	CSR=/tmp/ssl_cert_sign_req-$$.csr
	openssl req -new -key /etc/ssl/local/ssl_certificate.key -out $CSR \
	  -sha256 -subj "/C=/ST=/L=/O=/CN=$DOMAIN"

	# Generate the self-signed certificate.
	CERT=/etc/ssl/local/ssl_certificate.crt
	openssl x509 -req -days 365 \
	  -in $CSR -signkey /etc/ssl/local/ssl_certificate.key -out $CERT

	# Delete the certificate signing request because it has no other purpose.
	rm -f $CSR
fi

# OUR SITE
##########

# Make a place to collect static files and to serve as the virtual root.
sudo -u site mkdir -p ../public_html/static

# Install dependencies.
sudo -u site pip3 install -r requirements.txt

# Fetch other dependencies.
sudo -u site deployment/fetch-vendor-resources.sh

# Create database / migrate database.
# TODO: Get rid of this in a real production environment because we should
# not touch the production database unless someone says so.
sudo -u site python3 manage.py migrate

# Create an 'admin' user.
#python3 manage.py createsuperuser --username=admin --email=admin@$DOMAIN --noinput
# gain access with: ./manage.py changepassword admin

# Collect static files to get ready to launch.
sudo -u site python3 manage.py collectstatic --noinput

# Supervisor, which runs uwsgi
ln -sf `pwd`/deployment/supervisor.conf /etc/supervisor/conf.d/q.govready.com.conf
service supervisor restart

# Restart nginx.
service nginx restart

