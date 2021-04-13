#!/bin/bash

# This file is for Ubuntu

# Install required OS packages for GovReady-Q.
# Run as root
# Usage:
#   ./install-os-packages.sh

OS="Ubuntu"

echo "Installing required $OS packages for GovReady-Q..."

apt-get update

# Install dependencies
DEBIAN_FRONTEND=noninteractive \
apt-get install -y \
unzip git curl jq \
python3 python3-pip python3-venv \
python3-yaml \
graphviz pandoc \
gunicorn \
language-pack-en-base language-pack-en

# Upgrade to pandoc to version 2.9 or higher
wget https://github.com/jgm/pandoc/releases/download/2.13/pandoc-2.13-linux-amd64.tar.gz
tar xvzf pandoc-2.13-linux-amd64.tar.gz
mv pandoc-2.13/bin/* /usr/local/bin
rm -Rf pandpandoc-2.13
rm pandoc-2.13-linux-amd64.tar.gz

# Optionally install supervisord for monitoring and restarting GovReady-q; and NGINX as a reverse proxy
apt-get install -y supervisor nginx
