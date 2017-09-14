#!/bin/bash

# Add a built-in AppSource that has an entry for the GovReady
# sample apps and an entry for loading apps from /mnt/apps which
# the user starting the container may want to bind-mount to a
# directory on the host for building their own apps.
mkdir -p /mnt/apps
python manage.py loaddata appsources.json

# Set up an initial admin user and an organization and add the
# user to the organization.
python manage.py first_run
