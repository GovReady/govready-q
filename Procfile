web: python manage.py migrate --no-input && python manage.py load_modules && $NEW_RELIC_START gunicorn siteapp.wsgi --access-logfile -
