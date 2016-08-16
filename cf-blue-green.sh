#!/bin/bash
set -euf -o pipefail

USAGE="$0 appname"
if [ $# -lt 1 ]; then
  printf "Error: appname is required, e.g.:\n\t$USAGE\n" >&2
  exit 1
fi

APPNAME=$1

finally () {
  rm -f ${APP_NAME}_manifest.yml
}

on_fail () {
  finally
  echo "DEPLOY FAILED - you may need to check 'cf apps' and 'cf routes' and do manual cleanup"
}

trap on_fail ERR
cf create-app-manifest $APPNAME
cf zero-downtime-push $APPNAME -f ${APPNAME}_manifest.yml
finally
echo "DONE"
