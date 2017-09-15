# Generate an environment.json file. Use the jq
# tool to ensure that we produce valid JSON from
# the environment variables.
mkdir -p local
echo "{ }" \
	| jq ".debug = true" \
	| jq ".host = $(echo ${ADDRESS-localhost:8000} | jq -R .)" \
	| jq ".https = ${HTTPS-false}" \
	| jq ".[\"single-organization\"] = \"main\"" \
	| jq ".db = $(echo ${DBURL} | jq -R .)" \
	> local/environment.json
if [ ! -z "$EMAIL_HOST" ]; then
	cat local/environment.json \
	| jq ".email.host = $(echo ${EMAIL_HOST} | jq -R .)" \
	| jq ".email.port = $(echo ${EMAIL_PORT} | jq -R .)" \
	| jq ".email.user = $(echo ${EMAIL_USER} | jq -R .)" \
	| jq ".email.pw = $(echo ${EMAIL_PW} | jq -R .)" \
	| jq ".email.domain = $(echo ${EMAIL_DOMAIN} | jq -R .)" \
	> local/environment.json
fi

# See first_run.sh. This directory must be created
# every time the container starts after the AppSource
# fixture has been loaded.
mkdir -p /mnt/apps

# Initialize the database and start the server.
python manage.py migrate
python manage.py load_modules
python manage.py runserver 0.0.0.0:8000
