# Generate an environment.json file.
mkdir -p local
cat > local/environment.json << EOF;
{
  "debug": true,
  "host": "${HOSTANDPORT-localhost:8000}",
  "https": ${HTTPS-false},
  "db": "$DATABASEURL",
  "single-organization": "main"
}
EOF

# Initialize the database and start the server.
python manage.py migrate
python manage.py load_modules
python manage.py runserver 0.0.0.0:8000
