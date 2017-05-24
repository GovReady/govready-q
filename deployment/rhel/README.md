# Deploying Q to Red Hat Enterprise Linux

## Preparing System Packages

Ensure `pip` and `psql` command line tools are installed:

    yum install python34-pip postgresql

(Our update script in `deployment/rhel/update.sh` uses `killall` to kick the Django Python process, which is provided by the psmisc package.

Q calls out to `git` to fetch apps from git repositories, but that requires git version 2 or later because of the use of the GIT_SSH_COMMAND environment variable. RHEL stock git is version 1. Switch it to version 2+ by using the IUS package:

    yum remove git
    yum install git2u


## Preparing Q Source Code

Create a UNIX user named `govready-q` and a deploy key to add to the Github repository:

    # Create user.
    useradd govready-q -c "govready-q"
    
    # Switch to user's home directory.
    sudo su govready-q
    cd /home/govready-q
    chmod a+rx . # so that Apache can read static files

    # Create deployment key without a passphrase.
    ssh-keygen -t rsa -b 2096 -C "govready-q_deploy_key"
    cat ~/.ssh/id_rsa.pub
    # add this to the govready-q Github repository so the machine can access the source code

Deploy GovReady-Q source code:

    git clone git@github.com:GovReady/govready-q.git
    cd govready-q
    
    # Install prerequisites for cryptography package per https://cryptography.io/en/latest/installation/. (You probably need to jump out of being the govready-q user for this line, then come back.)
    sudo yum install gcc libffi-devel python34-devel openssl-devel
    
    # Install pip packages
    pip3 install --user -r requirements.txt
    
    # Install other static dependencies.
    ./fetch-vendor-resources.sh
    
    # Configure `local/environment.json` 
    # Skipping for the moment to do default install with sqlite
    python3 manage.py migrate
    python3 manage.py load_modules
    python3 manage.py createsuperuser

## Setting Up the Database Server

### On the database server

On the database server, set up TLS connections. In `/var/lib/pgsql/data/postgresql.conf`, enable TLS by changing the ssl option to

    ssl = on 
      
and enable remote connections by binding to all interfaces:

    listen_addresses = '*'
      
Generate a self-signed certificate:

    openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /var/lib/pgsql/data/server.key -out /var/lib/pgsql/data/server.crt -subj '/C=US/CN=dbserver.hostname.com'
    chmod 600 /var/lib/pgsql/data/server.{key,crt}
    chown postgres.postgres /var/lib/pgsql/data/server.{key,crt}
    
Copy the certificate to the web server so that the web server can make trusted connections to the database server:

    cat /var/lib/pgsql/data/server.crt
    # place on web server at /home/govready-q/pgsql.crt
    
Enable remote connections to the database *only* from the web server and *only* encrypted with TLS by editing `/var/lib/pgsql/data/pg_hba.conf` and adding the line:

    hostssl all all webserver.hostname.com md5
    
Then restart the database:

    service postgresql restart

Then set up the user and database (both named `govready_q`):

    sudo -iu postgres createuser -P govready_q
    # paste a long random password
    
    sudo -iu postgres createdb govready_q

### On the web server
    
On the web server, now check that secure connections can be made:

    psql "postgresql://govready_q@dbserver.hostname.com/govready_q?sslmode=verify-full&sslrootcert=/home/govready-q/pgsql.crt"

(It should fail if the TLS certificate file is not provided, if sslmode is set to `disable`, if a different user or database is given, or if the wrong password is given.)

Then in our GovReady Q `local/environment.json` file, configure the database (replace `THEPASSWORDHERE`) by setting the following key:

        "db": "postgresql://govready_q:THEPASSWORDHERE@dbserver.hostname.com/govready_q?sslmode=verify-full&sslrootcert=/home/govready-q/pgsql.crt",

(Make sure the environment.json file is not world-readable.)

Then initialize the database content:

    pip3 install --user psycopg2
    python3 manage.py migrate
    python3 manage.py load_modules
    python3 manage.py createsuperuser

## Setting Up Apache & uWSGI

Symlink the Apache config into place:

    ln -s /home/govready-q/govready-q/deployment/rhel/apache.conf /etc/httpd/conf.d/govready-q.conf

The locations of a TLS key and certificate are specified in the Apache config file. Put a TLS key and certificate there!

Install `supervisor` which will keep the Python/Django process running and symlink our supervisor config into place:

    # as root
    yum install supervisor
    ln -s /home/govready-q/govready-q/deployment/rhel/supervisor.ini /etc/supervisord.d/govready-q.ini

    # as the govready-q user
    pip3 install --user uwsgi

Restart services:

    service supervisord restart
    service httpd restart

## Updating Deployment

When there are changes to the GovReady Q software, pull new sources and restart processes with:

    sudo -iu govready-q /home/govready-q/govready-q/deployment/rhel/update.sh
    
As root, you can also restart just the Python/Django process:    

    sudo supervisorctl restart app-uwsgi
    
But this won't do a full update so don't normally do that (it won't restart the separate notifications process or generate static assets, etc.).
