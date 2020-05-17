#!/bin/bash

set -euf -o pipefail # abort script on error

# Defaults
##########

# run the script be non-interactively?
# default is yes, run interactively
NONINTERACTIVE=

# Parse command-line arguments
##############################

while [ $# -gt 0 ]; do
  case "$1" in
    --non-interactive)
      NONINTERACTIVE=1
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

# indicate mode
if [ $NONINTERACTIVE ];
then
	echo "Installing GovReady-Q in non-interactive mode..."
else
	echo "Installing GovReady-Q in interactive mode (default)..."
fi

# Check that the database is ready. The docker exec command
# writes out a 'ready' file once migrations are finished.
while [ ! -f /tmp/govready-q-is-ready ]; do
	echo "Waiting for the database to finish initializing..."
	sleep 3
done

# Set up an initial admin user and an organization and add the
# user to the organization. Do this first because it returns
# a non-zero exit code if the database is not yet ready, causing
# this script to exit.
#
# Also: Add built-in AppSources that has an entry for the GovReady
# sample apps and an entry for loading apps from /usr/src/app/q-files
# which the user starting the container may want to bind-mount to a
# directory on the host for building their own apps. That directory
# must exist and is created in dockerfile_exec.sh.d

if [ $NONINTERACTIVE ];
then
	# python3 manage.py first_run --non-interactive
	python3.6 manage.py first_run --non-interactive
else
	# python3 manage.py first_run
	python3.6 manage.py first_run
fi
