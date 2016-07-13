#!/bin/bash

echo "------------- Run migration"
python manage.py migrate --noinput

echo "------------- Load modules"
python manage.py load_modules
