python manage.py migrate --noinput

python manage.py load_modules

gunicorn siteapp.wsgi
