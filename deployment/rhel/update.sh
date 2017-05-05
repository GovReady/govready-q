#!/bin/bash

# Change to the parent directory of the directory that contains this script.
cd $(dirname $(dirname $(dirname $(readlink -m $0))))

# Pull from git.
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa_govready-q" git pull --rebase &&

# Run database migrations.
python3 manage.py migrate &&

# Load updated modules into database.
python3 manage.py load_modules &&

# Extract static assets.
python3 manage.py collectstatic --noinput &&

# Kick the processes to reload modules.
killall -HUP /home/govready-q/.local/bin/uwsgi
pkill -f send_notification_emails
