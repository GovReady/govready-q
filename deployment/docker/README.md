# Dockerized Q - Version 1

A demo of GovReady Q is available on the Docker Hub at [https://hub.docker.com/r/govready/govready-q/](https://hub.docker.com/r/govready/govready-q/).

## Running

Start the container in the background:

	CONTAINER=$(docker container run --detach -p 8000:8000 govready/govready-q)

Create a Django database superuser and set up your first organization:

	docker container exec -it $CONTAINER ./first_run.sh

Visit your organization in your web browser at:

	http://localhost:8000/

To pause and restart the container without destroying its data:

	docker container stop $CONTAINER
	docker container start $CONTAINER

To destroy the container and all user data entered into Q:

	docker container rm -f $CONTAINER

If you are using the Docker image to develop your own compliance apps, then
you will need to bind-mount a directory on your (host) system as a directory
within the container so that the container can see your app YAML files. To
do so, start the container with this command instead:

	CONTAINER=$(docker container run --detach -p 8000:8000 --mount type=bind,src=/absolute/path/to/apps,dst=/mnt/apps govready/govready-q)

Substitute for `/absolute/path/to/apps` the absolute path to a directory containing
GovReady-Q Compliane Apps. This directory should have subdirectories for each of
your apps. For instance, you would have a file at `/absolute/path/to/apps/my_app/app.yaml`.

Notes:

* The Q database is only persisted within the container. The database will persist between `docker container stop`/`docker container start` commands, but when the container is removed from Docker (i.e. using `docker container rm`) the Q data will be destroyed.
* The Q instance cannot send email until it is configured to use a transactional mail provider like Mailgun. (TODO: How?)
* This image is not meant to be used for a public website because it uses Django's debug server to serve the site with `DEBUG = True`.

## Building and publishing the Docker image

You may build the Docker image locally from the current source code rather than obtaining it from the Docker Hub. In the root directory of this repository, build the Docker image:

	docker image build --tag govready/govready-q .

If you are a GovReady team member, you can then push the image to hub.docker.com:

	docker image push govready/govready-q

TODO:

* Remove `"debug": true` from environment.json when we figure out how to serve static assets with `manage.py runserver`.
