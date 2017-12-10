# Launching with Docker

A demo of GovReady Q is available on the Docker Hub at [https://hub.docker.com/r/govready/govready-q/](https://hub.docker.com/r/govready/govready-q/).

## Running

Make sure you first [install Docker](https://docs.docker.com/engine/installation/) and, if appropriate, [grant non-root users access to run Docker containers](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

Start the container in the background:

	docker container run --name govready-q --detach -p 8000:8000 govready/govready-q

For more complex setups, using our run script instead will be easier:

	wget https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh
	./docker_container_run.sh

Visit your GovReady-Q site in your web browser at:

	http://localhost:8000/

It may not load at first as it initializes your database for the first time. Wait for the site to become available.
Because of HTTP Host header checking, you must use `localhost` to access the site or another hostname if configured
using the `--address` option documented below.

If the site does not come up, check the container logs for an error message:
	
	docker container logs govready-q

With the container started and the database initialized, run our first-run script to create a Django database superuser and set up your first organization:

	docker container exec -it govready-q ./first_run.sh

To pause and restart the container without destroying its data:

	docker container stop govready-q
	docker container start govready-q

To destroy the container and all user data entered into Q:

	docker container rm -f govready-q

Notes:

* The Q database is only persisted within the container by default. The database will persist between `docker container stop`/`docker container start` commands, but when the container is removed from Docker (i.e. using `docker container rm`) the Q data will be destroyed. See the _Persistent database_ section below for connecting to a database outside of the container.
* The Q instance cannot send email or receive comment replies until it is configured to use a transactional mail provider like Mailgun -- see below.
* This image is not meant to be used for a public website because it uses Django's debug server to serve the site with `DEBUG = True`.

## Advanced configuration

Advanced container options can be set with command-line arguments to our container run script:

	./docker_container_run.sh ...additional arguments here...

### Changing the hostname and port

#### The public address (as users see it)

The container will run at `localhost:8000` by default, it will only be accessible from the
host machine, and because of HTTP Host header checking you must visit GovReady-Q using the
same hostname it is configured to run at (so, with default settings, visiting `127.0.0.1`
instead of `localhost` will result in an error).

You may change the hostname and port of the GovReady-Q server using:

	--address q.mydomain.com:80

If the Docker container is behind a proxy, then `--address` specifies the public address
that end-users will use to access GovReady-Q. This may differ from the address and port that the container is accessed at on your organization's network, which is set using `--bind`.

Add `--https` if end users will access GovReady-Q with https: URLs.

#### The address that the container is bound to

Use `--bind IP:PORT` to control how the listening socket is created on the host machine.
The default value of `--bind` is `127.0.0.1` and the port from `--address`, or `127.0.0.1:8000` if
`--address` isn't given. If the host machine is behind a proxy, use `--bind` to control the
network interface and port that Docker will forward to the GovReady-Q container.

	--bind 10.0.0.5:6543

### Persistent database

In a production environment it is important to have GovReady-Q connect to a
persistent database instead of the database stored inside the container,
which will be destroyed when the container is destroyed. There are two methods
for connecting to a persistent database.

#### Sqlite file

You can use a Sqlite file stored on the host machine:

	--sqlitedb /path/to/govready-q-database.sqlite

You must specify an absolute path.

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

	--dburl postgres://$DBUSER:$DBPASSWORD@$DBHOST/$DBDATABASE

where `$DBHOST` is the hostname of the database server, `$DBDATABASE` is the name of the database, and `$DBUSER` and `$DBPASSWORD` are the credentials for the database.

### Configuring email

GovReady-Q sends outbound emails for notifications about invitations and discussions.
It also receives inbound emails --- replies to dicussion notifications can be used to
post discussion comments by email.

To configure outbound email, add:

	--email-host smtp.company.org --email-port 587 --email-user ... --email-pw ... --email-domain q.company.org

`--email-domain` sets the hostname used in the email address of outbound email. The other arguments set the SMTP relay server details.

Some of GovReady-Q's outbound emails can be replied to. When a user replies to a notification of a discussion comment, the reply's body is post as a new comment on the discussion. Currently we only support an incoming notification hook from Mailgun, and it is not yet configurable for the docker deployment. TODO

### Container management and other options

Use `--name NAME` to specify an alternate name for the container. The default is `govready-q`.

Use `--relaunch` to remove an existing container of the same name before launching
the new one, if an existing container of the same name exists. This simply runs
`docker container rm -f NAME`.

Add `--debug` to start GovReady-Q in DEBUG mode, which enables nicer error messages. Do not use in production.

### Developing compliance apps

If you are using the Docker image to develop your own compliance apps, then
you will need to bind-mount a directory on your (host) system as a directory
within the container so that the container can see your app YAML files. To
do so, start the container with the additional command-line argument:

	--appsdevdir /path/to/apps

The directory may be empty but it must exist, and you must specify it as an
absolute path (due to a Docker limitation). If the directory is not empty,
it should have subdirectories for each of your apps. For instance,
you would have a YAML file at `/path/to/apps/my_app/app.yaml`.

To create your first app, you can run

	docker container exec -it govready-q ./manage.py compliance_app host your_new_app_name

Replace `your_new_app_name` with an app identifier, which may contain letters,
numbers, dashes, and underscores. `host` is always just `host` --- don't change
that.

If your new app does not appear in the compliance apps catalog, you may need
to force the app catalog cache to be cleared by restarting the container:

	docker container restart govready-q


## Updating to a new release of GovReady-Q

Periodically there will be a new release of GovReady-Q as an new image on the Docker Hub. Updating is easy by re-running the same commands again.

1) There may be an update to `docker_container_run.sh`. Since this script is not a part of the Docker image, you will need to get it again from this Github repository.

2) You should be using a persistent database as described above. When using a persistent database, it is safe to detroy the `govready-q` Docker container and start a new one to deploy an update.

3) Use the same arguments to `docker_container_run.sh` as when you started the container the last time, but add `--relaunch` to kill the previous container --- you cannot have two containers with the same name or two containers listening on the same port. (You can change the name and port, as described above, if you would like to keep the old container running.)

4) When the new container starts, database migrations will be applied, if applicable.

For example:

	# Update docker_container_run.sh, replacing the old script (with -O).
	wget -O docker_container_run.sh \
	    https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh
	
	# Remove old container and launch updated container.
	./docker_container_run.sh --relaunch [your same command-line arguments]


## Building and publishing the Docker image for GovReady-Q maintainers

You may build the Docker image locally from the current source code rather than obtaining it from the Docker Hub. In the root directory of this repository, build the Docker image:

	docker image build --tag govready/govready-q .

If you are a GovReady team member, you can then push the image to hub.docker.com:

	docker login
	# respond to prompts with credentials
	docker image push govready/govready-q
