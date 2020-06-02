#!/bin/bash

# This file is for Ubuntu

# Install and configure PostgreSQL.
# Run as root or user with sudo permissions
# Usage:
#   ./install-os-packages.sh

OS="Ubuntu"
DBUSER="govready_q"
DATABASE=$DBUSER

echo "Installing required $OS packages for PostgreSQL..."
apt-get update
# Install dependencies
sudo apt install -y postgresql postgresql-contrib

# Create the database user account for GovReady-Q
sudo -iu postgres createuser -P $DBUSER
# Paste a long random password when prompted

# Create the database for GovReady-Q
# Postgres’s default permissions automatically grant users access to a database of the same name.
sudo -iu postgres createdb $DATABASE

# Print the configuration string with password hidden
echo "PostgreSQL installed and configured."
echo "Note the following for local/environment.json file (password hidden):"
echo "postgres://$DBUSER:XXXXXXXX@localhost:5432/$DATABASE"
