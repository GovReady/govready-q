# Generate an environment.json file.
mkdir -p local
cat > local/environment.json << EOF;
{
  "debug": true,
  "host": "${ADDRESS-localhost:8000}",
  "https": ${HTTPS-false},
  "db": "$DBURL",
  "single-organization": "main"
}
EOF

echo "Environment file:"
cat local/environment.json

# Initialize the database and start the server.
python manage.py migrate
python manage.py load_modules
python manage.py runserver 0.0.0.0:8000
