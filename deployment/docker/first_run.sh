#!/bin/bash

set -euf -o pipefail # abort script on error

# Check that the database is ready. The docker exec command
# writes out a 'ready' file once migrations are finished.
while [ ! -f ready ]; do
	echo "Waiting for the database to finish initializing..."
	sleep 3
done

# Set up an initial admin user and an organization and add the
# user to the organization. Do this first because it returns
# a non-zero exit code if the database is not yet ready, causing
# this script to exit.
#
# Also: Add built-in AppSources that has an entry for the GovReady
# sample apps and an entry for loading apps from /mnt/apps which
# the user starting the container may want to bind-mount to a
# directory on the host for building their own apps. That directory
# must exist and is created in dockerfile_exec.sh.
python3.6 manage.py first_run

