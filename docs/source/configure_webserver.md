# Configuring a Reverse Proxy Webserver for Production Use

## Setting Up Apache & uWSGI

Install Apache 2.x with SSL (back to being root):

	yum install httpd mod_ssl

Copy the Apache config into place:

    cp /home/govready-q/govready-q/deployment/rhel/apache.conf /etc/httpd/conf.d/govready-q.conf

And then edit the file replacing `q.govready.com` and `*.govready.com` with your hostnames.

If you don't have a TLS certificate ready to use, create a self-signed certificate (replacing `webserver.hostname.com` with your hostname):

    openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /home/govready-q/ssl_certificate.key -out /home/govready-q/ssl_certificate.crt -subj '/CN=webserver.hostname.com'
    chmod 600 /home/govready-q/ssl_certificate.{key,crt}
    chown apache.apache /home/govready-q/ssl_certificate.{key,crt}

If SELinux is enabled (`sestatus` shows `SELinux status: enabled`), grant the Apache process access to these files as well as the site's static files:

	chcon -v -R --type=httpd_sys_content_t /home/govready-q/govready-q/deployment/rhel/apache.conf /home/govready-q/ssl_certificate.{key,crt} /home/govready-q/public_html

and grant Apache permission to make network connections so that it can connect to the Python/uwsgi backend running GovReady-Q:

	setsebool httpd_can_network_connect true

Install `supervisor` which will keep the Python/Django process running and symlink our supervisor config into place:

    yum install supervisor
    ln -s /home/govready-q/govready-q/deployment/rhel/supervisor.ini /etc/supervisord.d/govready-q.ini

Restart services:

    service supervisord restart
    service httpd restart

And if necessary open the web ports:

	firewall-cmd --zone=public --add-port=80/tcp --permanent
	firewall-cmd --zone=public --add-port=443/tcp --permanent
	firewall-cmd --reload

GovReady-Q should now be running and accessible at your domain name. Follow the instructions in the [main README.md](https://github.com/GovReady/govready-q/blob/master/README.md) for creating your first organization.

### Setting up an HTTPS Certificate

The instructions above created a self-signed certificate to get the website up and running. To use Let's Encrypt to automatically provision a real certificate, install and run `certbot`:

	yum install -y python-certbot-apache
	certbot --apache -d webserver.hostname.com
	# and follow the prompts

Then set it to automatically renew certificates as needed:

	# edit root's crontab
	crontab -e

	# insert at end:
	30 2 * * * /usr/bin/certbot renew >> /var/log/le-renew.log

## Setting up Nginx

Configure nginx to use nginx.conf in the govready-q directory:

	# Turn off nginx's default website.
	rm -f /etc/nginx/sites-enabled/default

	# Put in our nginx site config.
	ln -sf /home/govready-q/govready-q/deployment/ubuntu/nginx.conf /etc/nginx/sites-enabled/yourdomain.com

	service nginx restart

The nginx conf file assumes a certificate chain and private key are present at `/etc/ssl/local/ssl_certificate.crt/key`.

