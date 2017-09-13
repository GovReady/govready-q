#!/bin/bash

# This script simplifies what users need to know in
# order to launch our Docker container.

# Defaults.

IMAGE="govready/govready-q" # the image on hub.docker.com
PORT=8000 # the local port exposed for the web server
LOCALSQLITEDB=
APPSDEV_DIR=

# Parse command-line arguments.

getopt --test > /dev/null
if [[ $? -ne 4 ]]; then
    echo "Make sure getopt is installed before running this script (e.g. brew install gnu-getopt)."
    exit 1
fi
OPTIONS=
LONGOPTIONS=image:,port:,sqlitedb:,appsdevdir:
PARSED_OPTIONS=$(getopt --options=$OPTIONS --longoptions=$LONGOPTIONS --name "$0" -- "$@")
if [[ $? -ne 0 ]]; then exit 2; fi
eval set -- "$PARSED_OPTIONS"
while true; do
    case "$1" in
    	--image)
			IMAGE="$2"
			shift 2 ;;
        --port)
            PORT="$2"
            shift 2 ;;
        --sqlitedb)
			LOCALSQLITEDB="$2"
			shift 2 ;;
        --appsdevdir)
			APPSDEV_DIR="$2"
			shift 2 ;;
        --)
            shift
            break
            ;;
    esac
done

# Construct the docker container run arguments.

# General arguments.
ARGS="--detach"

# Name the container.
NAME="--name govready-q"

# Port forwarding, mapping a host port to the port in the container that the
# web server is running at (8000).
PORTFWD="-p $PORT:8000"

# The mount argument for having the Sqlite database stored on the host.
DBMNT=""
if [ ! -z "$LOCALSQLITEDB" ]; then
	touch $LOCALSQLITEDB # it may not exist but we don't want readlink to fail
	LOCALSQLITEDBABS=$(readlink -e $LOCALSQLITEDB) # Docker requires absolute path
	if [ -z "$LOCALSQLITEDBABS" ]; then
		echo "Invalid Path: $LOCALSQLITEDB"
		exit 1
	fi
	DBMNT="--mount type=bind,src=$LOCALSQLITEDBABS,dst=/usr/src/app/local/db.sqlite3"
fi

# The mount argument for accessing a local directory containing app YAML files.
# See appsources.json.
APPSMNT=""
if [ ! -z "$APPSDEV_DIR" ]; then
	APPSDEV_DIRABS=$(readlink -e $APPSDEV_DIR) # Docker requires absolute path
	if [ -z "$APPSDEV_DIRABS" ]; then
		echo "Invalid Path: $APPSDEV_DIR"
		exit 1
	fi
	APPSMNT="--mount type=bind,src=$APPSDEV_DIRABS,dst=/mnt/apps"
fi

# Go!
CMD="docker container run $ARGS $NAME $PORTFWD $DBMNT $APPSMNT $IMAGE"
echo $CMD
CONTAINER_ID=$($CMD)
if [[ $? -ne 0 ]]; then exit 2; fi
echo "GovReady-Q has been started!"
