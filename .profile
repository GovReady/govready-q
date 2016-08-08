#!/bin/bash

echo "Setting env variables from .profile.  These will not be"
echo "available from `cf env` or when connected via `cf ssh`"

NEW_RELIC_LICENSE_KEY=$(
  echo $VCAP_SERVICES | jq '.newrelic[0].credentials.licenseKey')
export NEW_RELIC_LICENSE_KEY
echo "added env variable NEW_RELIC_LICENSE_KEY: $NEW_RELIC_LICENSE_KEY"

# join appname-space as new relic app name:
NEW_RELIC_APP_NAME=$(
  echo $VCAP_APPLICATION | jq -r '.| .application_name, .space_name' | sed 'N;s/\n/-/')
export NEW_RELIC_APP_NAME
echo "added env variable NEW_RELIC_APP_NAME: $NEW_RELIC_APP_NAME"

NEW_RELIC_LOG="stdout"
export NEW_RELIC_LOG
echo "added env var NEW_RELIC_LOG: $NEW_RELIC_LOG"
