# Dockerized Q - Version 1

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

With the container started and the database initialized, run our first-run script to create a Django database superuser and set up your first organization:

	docker container exec -it govready-q ./first_run.sh

To pause and restart the container without destroying its data:

	docker container stop govready-q
	docker container start govready-q

To destroy the container and all user data entered into Q:

	docker container rm -f govready-q

Notes:

* The Q database is only persisted within the container by default. The database will persist between `docker container stop`/`docker container start` commands, but when the container is removed from Docker (i.e. using `docker container rm`) the Q data will be destroyed. See the _Persistent database_ section below for connecting to a database outside of the container.
* The Q instance cannot send email until it is configured to use a transactional mail provider like Mailgun. (TODO: How?)
* This image is not meant to be used for a public website because it uses Django's debug server to serve the site with `DEBUG = True`.

## Advanced configuration

Advanced container options can be set with command-line arguments to our container run script:

	deployment/docker/docker_container_run.sh ...additional arguments here...

### Changing the hostname and port

The container will run at `localhost:8000` by default, and because of HTTP Host header checking
you must visit GovReady-Q using the hostname it is configured to run at (so in this example,
substituting an IP address such as `127.0.0.1` for `localhost` will result in an error).

You may change the hostname and port that the container is running at using:

	--address q.mydomain.com:80

If the Docker container is behind a proxy, then `--address` should specify the public address
that end-users will use to access GovReady-Q and `--port` may be used if the Docker container
should listen on a different port:

	--port 8000

Add `--https` if the proxy is terminating HTTPS connections.

### Persistent database

In a production environment it is important to have GovReady-Q connect to a
persistent database instead of the database stored inside the container,
which will be destroyed when the container is destroyed. There are two methods
for connecting to a persistent database.

#### Sqlite file

You can use a Sqlite file stored on the host machine:

	--sqlitedb /path/to/govready-q-database.sqlite

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

Start the GovReady-Q container with the argument:

	--dburl postgres://$DBUSER:$DBPASSWORD@$DBHOST/$DBDATABASE

where `$DBHOST` is the hostname of the database server, `$DBDATABASE` is the name of the database, and `$DBUSER` and `$DBPASSWORD` are the credentials for the database.

#### Container management

Use `--name NAME` to specify an alternate name for the container. The default is `govready-q`.

Use `--relaunch` to remove an existing container of the same name before launching
the new one, if an existing container of the same name exists. This simply runs
`docker container rm -f NAME`.

### Developing compliance apps

If you are using the Docker image to develop your own compliance apps, then
you will need to bind-mount a directory on your (host) system as a directory
within the container so that the container can see your app YAML files. To
do so, start the container with the additional command-line argument:

	--appsdevdir /path/to/apps

This directory should have subdirectories for each of your apps. For instance,
you would have a YAML file at `/path/to/apps/my_app/app.yaml`.


## Building and publishing the Docker image for GovReady-Q maintainers

You may build the Docker image locally from the current source code rather than obtaining it from the Docker Hub. In the root directory of this repository, build the Docker image:

	docker image build --tag govready/govready-q .

If you are a GovReady team member, you can then push the image to hub.docker.com:

	docker image push govready/govready-q

TODO:

* Remove `"debug": true` from environment.json when we figure out how to serve static assets with `manage.py runserver`.
