# Dockerized Q

## Running

Start the container in the background:

	CONTAINER=$(docker container run --detach -p 8000:8000 govready/q)

Create a Django database superuser and set up your first organization:

	docker container exec -it $CONTAINER ./first_run.sh

Visit your organization in your web browser at:

	http://localhost:8000/

This image is not meant to be used for a public website.

## Building the Docker image

In the root of the Q source code, run:

	docker image build --tag govready/q .
	