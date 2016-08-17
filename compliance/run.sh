#!/bin/bash

set -euf -o pipefail -x

# BRANCH=${CIRCLE_BRANCH:-master}

cf api https://api.run.pivotal.io
cf auth $PWS_USER $PWS_PASS
cf target -o GovReady -s dev

cd compliance &&
  bundle exec inspec exec . --controls cf-dev-roles
