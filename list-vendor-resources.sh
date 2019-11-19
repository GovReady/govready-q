#!/bin/bash

set -euo pipefail

VENDOR=siteapp/static/vendor

ls -l `find $VENDOR -type f | sort -f`
