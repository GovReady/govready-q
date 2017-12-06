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
HOST=localhost
PORT=8000

# Set to 'true' if the site is running behind a proxy that
# is terminating HTTPS connections. Using "--https" sets
# this to true.
HTTPS=false

# The host interface and port the Docker container will bind to
# and listen on for incoming connections. Set with --bind HOST:PORT.
# Defaults to 127.0.0.1 and the port in $ADDRESS.
BIND=

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

# Allow the image to send email using a transactional email
# provider or other SMTP server.
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USER=
EMAIL_PW=
EMAIL_DOMAIN=

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
      # Split --address on a colon and store in HOST and PORT..
      IFS=':' read -r -a ADDRESS <<< "$2"
      HOST=${ADDRESS[0]-localhost}
      PORT=${ADDRESS[1]-80}
      shift 2 ;;
    --https)
      HTTPS=true
      shift 1 ;;
    --bind)
      BIND="$2"
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

    --email-host)
      EMAIL_HOST="$2"
      shift 2 ;;
    --email-port)
      EMAIL_PORT="$2"
      shift 2 ;;
    --email-user)
      EMAIL_USER="$2"
      shift 2 ;;
    --email-pw)
      EMAIL_PW="$2"
      shift 2 ;;
    --email-domain)
      EMAIL_DOMAIN="$2"
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
      PREV=$(docker container rm -f $NAME)
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

# If --bind is not specified, use 127.0.0.1 and the port from --address.
if [ -z "$BIND" ]; then
  BIND="127.0.0.1:$PORT"
fi

# Form the -p option, which maps host:port (an interface and host port)
# to a container port, which is always 8000. See dockerfile_exec.sh.
DASHP="-p $BIND:8000"

# Set environment variables for the Django process to use.
ENVS="-e HOST=$HOST -e PORT=$PORT -e HTTPS=$HTTPS -e DBURL=$DBURL"
ENVS="$ENVS -e EMAIL_HOST=$EMAIL_HOST -e EMAIL_PORT=$EMAIL_PORT -e EMAIL_USER=$EMAIL_USER -e EMAIL_PW=$EMAIL_PW -e EMAIL_DOMAIN=$EMAIL_DOMAIN"

# Add a mount argument for having the Sqlite database stored on the host.
# The path must be absolute (Docker mount requires absolute paths).
DBMNT=""
if [ ! -z "$SQLITEDB" ]; then
  touch $SQLITEDB # ensure path exists
  DBMNT="--mount type=bind,src=$SQLITEDB,dst=/usr/src/app/local/db.sqlite3"
fi

# Add a mount argument for accessing a local directory containing app YAML files.
# See appsources.json. The path must be absolute. For Docker it must exist, so
# we'll create it if needed.
APPSMNT=""
if [ ! -z "$APPSDEVDIR" ]; then
  mkdir -p $APPSDEVDIR
  APPSMNT="--mount type=bind,src=$APPSDEVDIR,dst=/mnt/apps"
fi

# Form the "docker container run command".
CMD="docker container run $ARGS $NAMEARG $DASHP $ENVS $DBMNT $APPSMNT $IMAGE"

# Echo it for debugging.
# Don't echo out of debugging because it may leak secrets.
#echo $CMD

# Execute and capture the output, which is a container ID.
CONTAINER_ID=$($CMD)
if [[ $? -ne 0 ]]; then exit 2; fi

# The container has been started but it'll be a moment before the
# http server is listening.
echo "GovReady-Q is starting..."
if [ ! -z "$NAME" ]; then
  echo "Container Name: $NAME"
fi
echo "Container ID: $CONTAINER_ID"
echo "Listening on: $BIND"

# Check that the database is ready. The docker exec command
# writes out a 'ready' file once migrations are finished,
# and then it's probably another second before the Django
# server is listening.
while ! docker container exec $NAME test -f ready; do
  echo "Waiting for GovReady-Q to come online..."
  sleep 3
done
sleep 1

echo "GovReady-Q has been started!"
echo -n "URL: http"
if [ "$HTTPS" == true ]; then echo -n s; fi
echo "://$ADDRESS"
