#!/bin/bash

VENDOR=siteapp/static/vendor

ls -l `find $VENDOR -type f | sort -f`
