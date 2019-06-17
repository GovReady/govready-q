# Deploying with Docker

| Container                 | Where                                                                                                           |
|---------------------------|-----------------------------------------------------------------------------------------------------------------|
| Current Release on Docker | [https://hub.docker.com/r/govready/govready-q/](https://hub.docker.com/r/govready/govready-q/)                  |
| Release 0.9.0.dev on Docker | [https://hub.docker.com/r/govready/govready-0.9.0.dev/](https://hub.docker.com/r/govready/govready-q-0.9.0.dev/)                  |
| Nightly Build on Docker   | [https://hub.docker.com/r/govready/govready-q-nightly/](https://hub.docker.com/r/govready/govready-q-nightly/)  |

## Quickstart

.. container:: content-tabs

    .. tab-container:: docker
        :title: Docker

        .. rubric:: Installing with Docker

        Make sure you first install Docker (https://docs.docker.com/engine/installation/) and, if appropriate, grant non-root users access to run Docker containers (https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

        .. rubric:: Start

        .. code-block:: bash

            # Run the docker container in detached mode
            docker container run --name govready-q --detach -p 8000:8000 govready/govready-q

            # Create admin account and organization data
            docker container exec -it govready-q first_run

            # Stop, start container (when needed)
            docker container stop govready-q
            docker container start govready-q

            # View logs - useful if site does not appear
            docker container logs govready-q

            # To destroy the container and all user data entered into Q
            docker container rm -f govready-q


        Visit your GovReady-Q site in your web browser at:

            http://localhost:8000/


## Additional Details

### Notes and Common Issues

Your GovReady-Q site will not load immediately, as GovReady-Q initializes your database for the first time. Wait for the site to become available.

Because of HTTP Host header checking, you must use `localhost` to access the site, or another hostname if configured using the `--address` option documented below.

If the site does not come up, check the container logs for an error message:
	
	docker container logs govready-q

The GovReady-Q default SQLite database created within a Docker container exists only for the duration of the container's lifetime. The database will persist between `docker container stop`/`docker container start` commands, but when the container is removed from Docker (i.e. using `docker container rm`) the database will be destroyed. See the _Persistent database_ section below for connecting to a database outside of the container for production data. 

The default Govready-Q instance cannot send email or receive comment replies until it is configured to use a transactional mail provider like Mailgun -- see below.

The default Govready-Q instance is configured to non-debug mode (Django `DEBUG=false`), which is the recommended setting for a public website. The instance can be set to debug mode at runtime -- see below.

### Advanced configuration of GovReady-Q inside Docker

For more complex setups, using our run script instead will be easier:

	wget https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh
	./docker_container_run.sh

Advanced container options can be set with command-line arguments to our container run script:

	./docker_container_run.sh ...GovReady-Q arguments... -- ...Docker arguments...

#### Changing the hostname and port

##### The public address (as users see it)

The container will run at `localhost:8000` by default, it will only be accessible from the
host machine, and because of HTTP Host header checking you must visit GovReady-Q using the
same hostname it is configured to run at (so, with default settings, visiting `127.0.0.1`
instead of `localhost` will result in an error).

You may change the hostname and port of the GovReady-Q server using:

	./docker_container_run.sh --address q.mydomain.com:80

If the Docker container is behind a proxy, then `--address` specifies the public address
that end-users will use to access GovReady-Q. This may differ from the address and port that the container is accessed at on your organization's network, which is set using `--bind`.

Add `--https` if end users will access GovReady-Q with https: URLs. This must be done through a proxy that accepts HTTPS connections and passes the requests using HTTP to the Docker container. See the `HTTPS` environment variable, below.

##### The address that the container is bound to

Use `--bind IP:PORT` to control how the listening socket is created on the host machine.
The default value of `--bind` is `127.0.0.1` and the port from `--address`, or `127.0.0.1:8000` if
`--address` isn't given. If the host machine is behind a proxy, use `--bind` to control the
network interface and port that Docker will forward to the GovReady-Q container.

	./docker_container_run.sh --bind 10.0.0.5:6543

### Persistent database

In a production environment it is important to have GovReady-Q connect to a
persistent database instead of the database stored inside the container,
which will be destroyed when the container is destroyed. There are two methods
for connecting to a persistent database.

#### Sqlite file

You can use a Sqlite file stored on the host machine:

	./docker_container_run.sh --sqlitedb /path/to/govready-q-database.sqlite

You must specify an absolute path. The path is mounted using a Docker bind mount into the container filesystem.

The file must be readable and writable by the container process, which is running as user 1000/group 1000. Although the container is running as a user isolated from the host environment, filesystem permissions for mounted files are based on comparing the raw user/group IDs of the file's owner/group on the host to the raw user/group ID of the process running in the container. Consider granting user 1000 read/write permission to the database using ACLs:

	setfacl -m u:1000:rw /path/to/govready-q-database.sqlite

Of course, do not do this if the host machine has a user 1000 that you do not trust.

#### Remote database

You can also connect to a database running on a remote system accessible to
the Docker container.

For instance, you might run a second Docker container holding a Postgres
server.

	DBPASSWORD=mysecretpassword
	docker container run --name govready-q-db -e POSTGRES_PASSWORD=$DBPASSWORD -d postgres
	DBHOST=$(docker container inspect govready-q-db | jq -r .[0].NetworkSettings.IPAddress)
	DBUSER=postgres
	DBDATABASE=postgres

(This example uses `jq`, a JSON parsing tool, to extract the IP address of the database container. You can install `jq` or just set `DBHOST` manually by looking for the IP address in `docker container inspect govready-q-db`.)

Start the GovReady-Q container with the argument:

	./docker_container_run.sh --dburl postgres://$DBUSER:$DBPASSWORD@$DBHOST/$DBDATABASE

where `$DBHOST` is the hostname of the database server, `$DBDATABASE` is the name of the database, and `$DBUSER` and `$DBPASSWORD` are the credentials for the database.

You can also use a MySQL or MariaDB server using the syntax `mysql://USER:PASSWORD@HOST:PORT/NAME`.

### Configuring email

GovReady-Q sends outbound emails for notifications about invitations and discussions.
It also receives inbound emails --- replies to discussion notifications can be used to
post discussion comments by email.

To configure outbound email, use:

	./docker_container_run.sh --email-host smtp.company.org --email-port 587 --email-user ... --email-pw ... --email-domain q.company.org

`--email-domain` sets the hostname used in the email address of outbound email. The other arguments set the SMTP relay server details.

Some of GovReady-Q's outbound emails can be replied to. When a user replies to a notification of a discussion comment, the reply's body is post as a new comment on the discussion. Currently we only support an incoming notification hook from Mailgun, and it is not yet configurable for the docker deployment. TODO

### Container management and other options

Other options that can be passed on the command-line are:

Use `--name NAME` to specify an alternate name for the container. The default is `govready-q`.

Use `--relaunch` to remove an existing container of the same name before launching
the new one, if an existing container of the same name exists. This simply runs
`docker container rm -f NAME`.

Add `--debug` to start GovReady-Q in DEBUG mode, which enables nicer error messages. Do not use in production.

You can additionally pass parameters to the `docker container run` command by separating the [Docker parameters](https://docs.docker.com/engine/reference/run/) from the GovReady-Q parameters with `--`, such as:

	./docker_container_run.sh --address q.mydomain.com:80 -- -e VAR=VALUE

### Adding and developing compliance apps

If you are using the Docker image to develop your own compliance apps, then
you will need to bind-mount a directory on your (host) system as a directory
within the container so that the container can see your app YAML files. To
do so, start the container with the additional command-line argument:

	--appsdevdir /path/to/apps

The directory may be empty but it must exist, and you must specify it as an
absolute path (due to a Docker limitation).

The directory and its contents must also be readable --- and writable, if you
intend to use GovReady-Q's authoring tools --- by the container process. The
container process is running as user 1000/group 1000. Although the container
is running as a user isolated from the host environment, filesystem permissions
for mounted files are based on comparing the raw user/group IDs of the file's
owner/group on the host to the raw user/group ID of the process running in the
container.  Consider granting user 1000 read/write permission to the files,
plus execute (i.e. browse) permission to the directories, in the mounted path
using ACLs:

	setfacl -R -m u:1000:rwX /path/to/apps

Of course, do not do this if the host machine has a user 1000 that you do not trust.

If the directory is not empty, it should have subdirectories for each of your apps.
For instance, you would have a YAML file at `/path/to/apps/my_app/app.yaml`.

To create your first app, you can run

	docker container exec -it govready-q python3.6 manage.py compliance_app host your_new_app_name

Replace `your_new_app_name` with an app identifier, which may contain letters,
numbers, dashes, and underscores. `host` is always just `host` --- don't change
that.

If your new app does not appear in the compliance apps catalog, you may need
to force the app catalog cache to be cleared by restarting the container:

	docker container restart govready-q

### Console and logs

The container's console, which can be accessed with

	docker container logs govready-q

shows the output of container's start-up commands including database migrations and process startup.

Additional log files are stored in /var/log within the container. These files contain access logs and other program output, including logs for unhandled error messages that appear as 500 Internal Server Error pages to end users. A special management command can be used to see the log files:

	docker container exec govready-q tail_logs

`tail_logs` takes the same arguments as Unix `tail`. For instance, add `-n 1000` to see the most recent 1,000 log lines, or add `-f` to continue to output the logs as the log files grow.

The log files can also be accessed by mounting `/var/log` with a Docker bind-mount or as a volume (and that's the only way to see the logs if `docker container exec` cannot be used in your environment).

### Production deployment of the Docker container

The GovReady-Q container runs several processes, including an HTTP/application server and a background process for sending notification emails.

### Secure deployments

The container's processes run exclusively as a non-root user with UID 1000 and GID 1000.

The container may be run with a read-only root filesystem (Docker's `--read-only` argument) so long as `/run`, `/tmp`, and `/var/log` are writable. When the `--dburl` argument is given to our `docker_container_run.sh` script, a read-only filesystem is activated using:

	--read-only --tmpfs /run --tmpfs /tmp --tmpfs /var/log

The three directories can be made writable either by being mounted as tmpfs temporary filesystems, as above, or using a bind mount or a Docker volume. In production environments where the container is launched without our script, it is recommended to use tempfs for `/run` and `/tmp` and to mount `/var/log` to a volume.


### Other management commands

See the [uWSGI](http://uwsgi-docs.readthedocs.io/) application server JSON process stats:

	docker container exec govready-q uwsgi_stats

### Updating to a new release of GovReady-Q

Periodically there will be a new release of GovReady-Q as an new image on the Docker Hub. Updating is easy by re-running the same commands again.

1) There may be an update to `docker_container_run.sh`. Since this script is not a part of the Docker image, you will need to get it again from this GitHub repository.

2) You should be using a persistent database as described above. When using a persistent database, it is safe to destroy the `govready-q` Docker container and start a new one to deploy an update.

3) Use the same arguments to `docker_container_run.sh` as when you started the container the last time, but add `--relaunch` to kill the previous container --- you cannot have two containers with the same name or two containers listening on the same port. (You can change the name and port, as described above, if you would like to keep the old container running.)

4) When the new container starts, database migrations will be applied, if applicable.

For example:

	# Update docker_container_run.sh, replacing the old script (with -O).
	wget -O docker_container_run.sh \
	    https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh
	
	# Remove old container and launch updated container.
	./docker_container_run.sh --relaunch [your same command-line arguments]


### Environment variables for launching the container without our run script

The following environment variables are used to configure the container when launching GovReady-Q using `docker run` or a container service (i.e., not when using our `docker_container_run.sh` helper script).

`HOST` - The domain name that GovReady-Q will be accessible at by end users. (Default: `localhost`)

`PORT` - The port that GovReady-Q will be accessed at by end users, typically either 80 (no HTTPS) or 443 (HTTPS). (Default: `8080`)

`HTTPS` - Set to `true` if GovReady-Q will be accessed by end users at an https: address.  This must be done through a proxy that accepts HTTPS connections and passes the requests using HTTP to the Docker container. The proxy must set the `X-Forwarded-Proto: https` header. It is also permissible for the proxy to forward HTTP requests, and those requests will be automatically redirected to the https: URL. (Default: `false`)

`DEBUG` - Set to `true` to run in Django debug mode. (Default: `false`)

`DBURL` - Set to a database connection string as described in [https://github.com/kennethreitz/dj-database-url](https://github.com/kennethreitz/dj-database-url). We recommend using PostgreSQL [using a TLS server certificate](https://www.postgresql.org/docs/9.1/static/libpq-ssl.html), e.g. `postgresql://user:password@dbhost/govready_q?sslmode=verify-full&sslrootcert=/path/to/pgsql.crt` (although you'll have to figure out how to get the server certificate accessible via the container filesystem). (Default: Not set, which means using a Sqlite database stored in the container at `/usr/src/app/local/database.sqlite`, which will be ephemeral if the path is not mounted to the host or a Docker volume.)

`ORGANIZATION_PARENT_DOMAIN` - If not set, GovReady-Q will be single-tenant and the database must be configured with a single organization whose subdomain is `main`. If set, GovReady-Q will be multi-tenant, serving a landing page and organization-specific sites on different domain names. A landing/signup page and the Django `/admin` site will be available at the domain name given in the `HOST` environment variable and organization sites will be served at subdomains of the `ORGANIZATION_PARENT_DOMAIN` domain name value. (Default: Not set).

`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PW`, and `EMAIL_DOMAIN` - For enabling outbound email. The host, port, username, and password settings specify a TLS-enabled SMTP server. `EMAIL_DOMAIN` is the domain name to use in outbound mail. (Default: Not set and outbound emails are dumped to logs for debugging.) To test the email configuration from the command-line, you can run `docker container exec -it govready-q python3.6 manage.py sendtestemail you@example.com`. If email is configured, you should not see any output and you should get a test email.

`FIRST_RUN` - If set to `1`, an administrator user will be created when the container launches and a randomly generated password will be given to the user and printed on the console, which will be visible in the container's logs. An organization with subdomain `main` will also be created.

`PROCESSES` - The number of concurrent requests that can be handled by the container. (Default: 4)

`SECRET_KEY` - The [Django SECRET_KEY](https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key) for session management. (Try [this tool](https://www.miniwebtool.com/django-secret-key-generator/) to generate one.)

`ADMINS` - The [Django ADMINS](https://docs.djangoproject.com/en/2.0/ref/settings/#admins) setting, passed as raw JSON. Example: `[["Admin Name 1", "admin1@example.com"], ["Admin Name 2", "admin2@example.com"]]`. (Default: Empty list, i.e. `[]`.)

`SYSLOG` - The host and port of a syslog-compatible log message sink. (Default: None.)

`MAILGUN_API_KEY` - An API key for Mailgun which is used to validate incoming webhook requests from Mailgun when an incoming email is received, when Mailgun is configured to handle incoming mail. (Default: None)

`BRANDING` (downstream packaging only): You may override the templates and stylesheets that are used for GovReady-Q's branding by setting this environment variable to the name of an installed Django app Python module (i.e. created using `manage.py startapp`) that holds templates and static files. No such app is provided in the GovReady-Q published Docker image, so this variable can only be used by downstream image maintainers.  See [Applying Custom Organization Branding](CustomBranding.html).

`PROXY_AUTHENTICATION_USER_HEADER` and `PROXY_AUTHENTICATION_EMAIL_HEADER`: GovReady-Q can be deployed behind a reverse proxy that authenticates users and passes the authenticated user's username and email address in HTTP headers. These environment variables correspond to the settings documented in [Enterprise Login](Environment.html#proxy-authentication-sever).

### Running tests

GovReady-Q's unit tests can be run within the Docker container. After building the image:

	docker container run --rm -it govready/govready-q:latest python3.6 manage.py test

Or once a Docker container running GovReady-Q is started (and named `govready-q`), use `exec` to begin a shell within the container, and then launch the unit tests:

	docker container exec -it govready-q bash
	python3.6 manage.py test guidedmodules

The functional tests run a headless Chromium web browser session. We welcome assistance figuring out how to get this to work in our Docker container. Chromium's process isolation capabilities seem to require special system privileges (i.e. `docker run --privileged --cap-add SYS_ADMIN`) or Chromium command-line flags (`--no-sandbox --disable-gpu`).

	yum install -y chromium chromedriver
	python3.6 manage.py test
	...
	selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start: exited abnormally
