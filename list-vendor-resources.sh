#!/bin/bash

# retrieve 'static' from local/environment.json
if [ -f local/environment.json ] ; then
  VENDOR=$(python -c "import json; f=open('local/environment.json', 'r'); env=json.load(f); print(env.get('static',''))")
fi

# if VENDOR not set above, use default
if [ -z "$VENDOR" ] ; then
  VENDOR=siteapp/static/vendor
fi

ls -l `find $VENDOR -type f | sort -f`
