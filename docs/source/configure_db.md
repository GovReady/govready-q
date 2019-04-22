# Setting up a Database for Production Workloads

## Setting Up the Postgres Database Server

This deployment script uses PostgreSQL but other database servers may be used.

### On the database server

On the database server, install Postgres:
	
	yum install postgresql-server postgresql-contrib
	postgresql-setup initdb

In `/var/lib/pgsql/data/postgresql.conf`, enable TLS connections by changing the `ssl` option to

    ssl = on 

and enable remote connections by binding to all interfaces:

    listen_addresses = '*'

Enable remote connections to the database *only* from the web server and *only* encrypted with TLS by editing `/var/lib/pgsql/data/pg_hba.conf` and adding the line (replacing the hostname with the hostname of the Q web server):

    hostssl all all webserver.hostname.com md5
    
Generate a self-signed certificate (replace `db.govready-q.internal` with the database server's hostname if possible):

    openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /var/lib/pgsql/data/server.key -out /var/lib/pgsql/data/server.crt -subj '/CN=db.govready-q.internal'
    chmod 600 /var/lib/pgsql/data/server.{key,crt}
    chown postgres.postgres /var/lib/pgsql/data/server.{key,crt}

Copy the certificate to the web server so that the web server can make trusted connections to the database server:

    cat /var/lib/pgsql/data/server.crt
    # place on web server at /home/govready-q/pgsql.crt
    
Then restart the database:

    service postgresql restart

Then set up the user and database (both named `govready_q`):

    sudo -iu postgres createuser -P govready_q
    # paste a long random password
    
    sudo -iu postgres createdb govready_q

Postgres's default permissions automatically grant users access to a database of the same name.

And if necessary, open the Postgres port:

	firewall-cmd --zone=public --add-port=5432/tcp --permanent
	firewall-cmd --reload

### On the web server
    
On the web server, now check that secure connections can be made:

    psql "postgresql://govready_q@dbserver.hostname.com/govready_q?sslmode=verify-full&sslrootcert=/home/govready-q/pgsql.crt"

(It should fail if the TLS certificate file is not provided, if sslmode is set to `disable`, if a different user or database is given, or if the wrong password is given.)

Then in our GovReady-Q `local/environment.json` file, configure the database (replace `THEPASSWORDHERE`) by setting the following key:

        "db": "postgresql://govready_q:THEPASSWORDHERE@dbserver.hostname.com/govready_q?sslmode=verify-full&sslrootcert=/home/govready-q/pgsql.crt",

Then initialize the database content:

    python3 manage.py migrate
    python3 manage.py load_modules

And generate static files:

	python3 manage.py collectstatic
