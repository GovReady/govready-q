#!/bin/bash

# This script simplifies what users need to know in
# order to launch our Docker container.

# Check that docker is installed and a version late
# enough to support the "docker container run" command.
if ! docker container 2>&1 | grep -q "Manage containers"; then
  echo "Please install the latest version of Docker from https://www.docker.com/community-edition."
  exit 1
fi

# Defaults
##########

# The image on hub.docker.com to use. Set with
# --image IMAGENAME. The default is:
IMAGE="govready/govready-q"

# The name for the newly run container. Set with
# --name NAME. If set to the empty string, no name
# is used. The default is:
NAME=govready-q

# The site's public address as would be entered in a
# web browser. Set with --address HOST:PORT. The port
# is optional if 80. The default is:
ADDRESS=localhost:8000

# Set to 'true' if the site is running behind a proxy that
# is terminating HTTPS connections. Using "--https" sets
# this to true.
HTTPS=false

# The port the Docker container will listen on. Set with
# --port PORT. Defaults to the port in $ADDRESS.
PORT=

# An absolute path to a Sqlite3 database file on the host machine
# to use as the database. Set with --sqlitedb /path/to/db.sqlite.
# Optional. Docker requires an absolute path and it must exist.
SQLITEDB=

# A database URL e.g. postgres://user:password@host/database.
# Set with --dburl URL. Optional.
DBURL=

# An absolute path on the host to a directory containing apps being
# developed. Set with --appsdevdir DIR. Optional.
# Docker requires an absolute path and it must exist.
APPSDEVDIR=

# If set, any existing container named $NAME will be killed
# with "docker container rm -f" first.
KILLEXISTING=

# Parse command-line arguments
##############################

while [ $# -gt 0 ]; do
  case "$1" in
    --image)
      IMAGE="$2"
      shift 2 ;;
    --name)
      NAME="$2"
      shift 2 ;;
    --address)
      ADDRESS="$2"
      shift 2 ;;
    --https)
      HTTPS=true
      shift 1 ;;
    --port)
      PORT="$2"
      shift 2 ;;
    --sqlitedb)
      SQLITEDB="$2"
      shift 2 ;;
    --dburl)
      DBURL="$2"
      shift 2 ;;
    --appsdevdir)
      APPSDEVDIR="$2"
      shift 2 ;;
    --relaunch)
      KILLEXISTING=1
      shift 1;;
    --)
        shift
        break
        ;;
    *)
      echo "Unrecognized command line option: $1";
      exit 1;
    esac
done

# Check if an existing container with the name we want is running.
if [ ! -z "$NAME" ]; then
  # docker container -f let's us specify a filter to find the ID of
  # of just the container named govready-q. The name filter by
  # default matches if the string is contained in the container name,
  # but we want an exact match. It supports ^ and $ from regex to make
  # it match on the start and end of the name. For an unknown reason the
  # container name starts with a "/" in filters (thanks StackOverflow).
  existing=$(docker container ls -q -a -f name="^/$NAME$")
  if [ ! -z "$existing" ]; then
    if [ -z "$KILLEXISTING" ]; then
      echo "There is already a Docker container named $NAME running."
      echo
      echo "You can kill it (including any data, if not using an external database) using:"
      echo "docker container rm -f $NAME"
      echo
      echo "Or start this script with --relaunch to kill it."
      exit 1
    else
      echo "Removing existing $NAME container..."
      PREV=$(docker container rm -f govready-q)
    fi
  fi
fi

# Check for an updated image.

docker image pull $IMAGE

# Construct the arguments to "docker container run".

# General arguments.
ARGS="--detach"

# Name the container.
if [ ! -z "$NAME" ]; then
  NAMEARG="--name $NAME"
fi

# Map a host port to port 8000 in the container, which is the port
# the Django process is listening on. Take from --address if --port
# is not specified.
if [ -z "$PORT" ]; then
  # Split --address on a colon and look at the part after the colon:
  IFS=':' read -r -a ADDRESSCOMPONENTS <<< "$ADDRESS"
  if [ ! -z "${ADDRESSCOMPONENTS[1]}" ]; then
    PORT=${ADDRESSCOMPONENTS[1]}
  else
    PORT=80
  fi
fi
PORT="-p $PORT:8000"

# Set environment variables for the Django process to use.
ENVS="-e ADDRESS=$ADDRESS -e HTTPS=$HTTPS -e DBURL=$DBURL"

# Add a mount argument for having the Sqlite database stored on the host.
# The path must be absolute (Docker mount requires absolute paths).
DBMNT=""
if [ ! -z "$SQLITEDB" ]; then
  touch $SQLITEDB # ensure path exists
  DBMNT="--mount type=bind,src=$SQLITEDB,dst=/usr/src/app/local/db.sqlite3"
fi

# Add a mount argument for accessing a local directory containing app YAML files.
# See appsources.json. The path must be absolute and must exist.
APPSMNT=""
if [ ! -z "$APPSDEVDIR" ]; then
  APPSMNT="--mount type=bind,src=$APPSDEVDIR,dst=/mnt/apps"
fi

# Form the "docker container run command".
CMD="docker container run $ARGS $NAMEARG $PORT $ENVS $DBMNT $APPSMNT $IMAGE"

# Echo it for debugging.
echo $CMD

# Execute and capture the output, which is a container ID.
CONTAINER_ID=$($CMD)
if [[ $? -ne 0 ]]; then exit 2; fi

# Say what happened.
echo "GovReady-Q has been started!"
if [ ! -z "$NAME" ]; then
  echo "Container Name: $NAME"
fi
echo "Container ID: $CONTAINER_ID"
echo -n "URL: http"
if [ "$HTTPS" == true ]; then echo -n s; fi
echo "://$ADDRESS"