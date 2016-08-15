#!/bin/bash

echo "Setting env variables from .profile.  These will not be"
echo "available from 'cf env' or when connected via 'cf ssh'"

export NEW_RELIC_LICENSE_KEY=$(
  echo $VCAP_SERVICES | jq -r '.newrelic[0].credentials.licenseKey')
echo "added env variable NEW_RELIC_LICENSE_KEY: $NEW_RELIC_LICENSE_KEY"

# join appname-space as new relic app name:
export NEW_RELIC_APP_NAME=$(
  echo $VCAP_APPLICATION | jq -r '.| .application_name, .space_name' | sed 'N;s/\n/-/')
echo "added env variable NEW_RELIC_APP_NAME: $NEW_RELIC_APP_NAME"

export NEW_RELIC_LOG="stdout"
echo "added env var NEW_RELIC_LOG: $NEW_RELIC_LOG"

if [ "$NEW_RELIC_LICENSE_KEY" = null ] || [ -z "$NEW_RELIC_LICENSE_KEY"]; then
  export NEW_RELIC_START=""
else
  export NEW_RELIC_START="newrelic-admin run-program"
fi
echo "added env var NEW_RELIC_START: $NEW_RELIC_START"
