#!/bin/bash

# This file is for Ubuntu

# Install required OS packages for GovReady-Q.
# Run as root
# Usage:
#   ./install-os-packages.sh

OS="Ubunto"

echo "Installing required $OS packages for GovReady-Q..."

apt-get update

# Install dependencies
DEBIAN_FRONTEND=noninteractive \
apt-get install -y \
unzip git curl jq \
python3 python3-pip \
python3-yaml \
graphviz pandoc \
language-pack-en-base language-pack-en

# Upgrade pip to version 20.1+
echo "Upgrading Python pip..."
python3 -m pip install --upgrade pip

