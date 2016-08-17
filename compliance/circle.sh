#!/bin/bash

# A wrapper script for running Compliance
# from a circleci node

set -euf -o pipefail -x

# select the control to use based on branch
BRANCH=${CIRCLE_BRANCH:-master}

case $BRANCH in
  master) space=dev;;
  prod)   space=prod;;
  *)      space=sandbox;;
esac

control=cf-$space-roles

cf api https://api.run.pivotal.io
cf auth $PWS_AUDITOR_USER $PWS_AUDITOR_PASS

cf target -o GovReady -s $space

cd compliance &&
  bundle exec inspec exec ./cf --controls $control
