#!/bin/bash

# Change to the parent directory of the directory that contains this script.
cd $(dirname $(dirname $(dirname $(readlink -m $0))))

# Pull from git.
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa_govready-q" git pull --rebase &&

# Install any new Python packages.
pip3 install --user -r requirements.txt &&

# Run database migrations.
python3 manage.py migrate &&

# Load updated modules into database.
python3 manage.py load_modules &&

# Extract static assets.
python3 manage.py collectstatic --noinput &&

# Kick the processes to reload modules.
pkill -u govready-q -f uwsgi
pkill -u govready-q -f send_notification_emails
