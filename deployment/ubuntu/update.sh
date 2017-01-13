#!/bin/bash

# Change to the parent directory of the directory that contains this script.
cd $(dirname $(dirname $(dirname $(readlink -m $0))))

# Pull from git.
git pull --rebase &&

# Run database migrations.
python3 manage.py migrate &&

# Load updated modules into database.
python3 manage.py load_modules &&

# Extract static assets.
python3 manage.py collectstatic --noinput &&

# Kick the processes to reload modules.
killall -HUP uwsgi_python3
pkill -f send_notification_emails
