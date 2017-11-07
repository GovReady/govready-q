#!/bin/bash

# This script checks the Python packages we're
# installing for security and freshness.

set -euf -o pipefail # abort script on error

# Install the latest pip-tools and pyup.io's safety tool.
pip3 install -U pip-tools safety

# Flatten out all of the dependencies of our dependencies to
# requirements.txt.
pip-compile --generate-hashes --output-file requirements.txt --no-header requirements.in

# Check packages for known vulnerabilities.
safety check -r requirements.txt

