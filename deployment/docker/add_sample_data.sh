#!/bin/bash

set -euf -o pipefail # abort script on error

# 0.8.6 sample data generation includes user creation. This
# argument allows the user to specify the password used for
# test user accounts
PASSWORD="$1"


# Generate a set of test users and organizations, and fill in
# assessments for those organizations
python3.6 manage.py populate --full --password "$1"
