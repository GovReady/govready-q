#!/bin/bash

# On a new machine, run:
# sudo deployment/setup.sh

#########################################

DOMAIN=q.govready.com

# THE SYSTEM
############

# Update system packages.
apt-get update && apt-get upgrade -y

# Get nginx from a PPA to get version 1.6 so we can support SPDY.
if [ ! -f /etc/apt/sources.list.d/nginx-stable-trusty.list ]; then
	sudo apt-get install -y software-properties-common # provides apt-add-repository
	sudo add-apt-repository -y ppa:nginx/stable
	sudo apt-get update
fi

# Install packages.
apt-get install -y \
	python3 python-virtualenv python3-pip \
	python3-yaml \
	nginx uwsgi-plugin-python3 supervisor \
	memcached

# Turn off nginx's default website.
rm -f /etc/nginx/sites-enabled/default

# Put in our nginx site config.
ln -sf `pwd`/deployment/nginx.conf /etc/nginx/sites-enabled/$DOMAIN

# Create DHparams for perfect forward secrecy as specified in the nginx config.
if [ ! -f /etc/ssl/local/dh2048.pem ]; then
	mkdir -p /etc/ssl/local
	openssl dhparam -out /etc/ssl/local/dh2048.pem 2048
fi

# Create a self-signed certificate so that nginx can start.
if [ ! -f /etc/ssl/local/ssl_certificate.key ]; then
	# Set the umask so the key file is never world-readable.
	(umask 077;
		openssl genrsa -out /etc/ssl/local/ssl_certificate.key 2048)
fi

# Generate a self-signed SSL certificate because things like nginx, dovecot,
# etc. won't even start without some certificate in place, and we need nginx
# so we can offer the user a control panel to install a better certificate.
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

# Install TLS cert provisioning tool.
apt-get install -y build-essential libssl-dev libffi-dev python3-dev python3-pip
pip3 install free_tls_certificates
cat > /etc/cron.daily/letsencrypt <<EOF;
free_tls_certificate $DOMAIN /etc/ssl/local/ssl_certificate.key /tmp/le_certificate.crt /home/ubuntu/public_html /home/ubuntu/acme-le-account \
	&& sudo mv /tmp/le_certificate.crt /etc/ssl/local/ssl_certificate.crt \
	&& sudo service nginx restart
rm -f /tmp/le_certificate.crt
EOF

# OUR SITE
##########

# Make a place to collect static files and to serve as the virtual root.
sudo -u site mkdir -p ../public_html/static

# Install dependencies.
sudo -u site pip3 install -r requirements.txt

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

# Procure real TLS certificate now that nginx is up.
bash /etc/cron.daily/letsencrypt
