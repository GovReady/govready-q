#!/bin/bash

set -euf -o pipefail # abort script on error

# Set up an initial admin user and an organization and add the
# user to the organization. Do this first because it returns
# a non-zero exit code if the database is not yet ready, causing
# this script to exit.
while ! python manage.py first_run; do
	# Database is not initialized yet.
	echo "Waiting for the database to finish initializing..."
	sleep 3
done

# Add a built-in AppSource that has an entry for the GovReady
# sample apps and an entry for loading apps from /mnt/apps which
# the user starting the container may want to bind-mount to a
# directory on the host for building their own apps.
mkdir -p /mnt/apps # must also happen every time container starts after the AppSource has been added
python manage.py loaddata appsources.json

