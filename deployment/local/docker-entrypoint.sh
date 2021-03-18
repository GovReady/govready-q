mkdir -p local
cp deployment/local/environment.json local/environment.json
pip install ipdb

if [ -f "local/vendor-packages.lock" ]; then
    echo "[ + ] Already have Vendor Files.  Skipping."
else
    echo "[ + ] Getting Vendor Files"
    ./fetch-vendor-resources.sh
    touch local/vendor-packages.lock
fi


echo "[ + ] Collect Static"
python3 manage.py collectstatic --noinput

echo "[ + ] Make migrations"
python3 manage.py makemigrations --noinput

# Apply database migrations
echo "[ + ] Apply database migrations"
python3 manage.py migrate --noinput

echo "[ + ] Load Modules"
python3 manage.py load_modules

echo "[ + ] Check"
python3 manage.py check

echo "[ + ] Making sure admin user exists"
cat <<EOF | python3 manage.py shell
from django.contrib.auth import get_user_model

User = get_user_model()  # get the currently active user model,

User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

if [ -f "local/first_run.lock" ]; then
    echo "[ + ] Execution of first_run previously completed.  Skipping."
else
    echo "[ + ] Executing first_run"
    python3 manage.py first_run --non-interactive
    touch local/first_run.lock
fi


# Start server
echo "[ + ] Starting server"
python3 manage.py runserver 0.0.0.0:8000