# This is the main entry point, i.e. process zero, of the
# Docker container.

# Generate a local/environment.json file. Use the jq
# tool to ensure that we produce valid JSON from
# the environment variables.
mkdir -p local

# What's the address (and port, if not 80) that end users
# will access the site at? If the HOST and PORT environment
# variables are set (and PORT is not 80), take the values
# from there, otherwise default to "localhost:8000".
ADDRESS="${HOST-localhost}:${PORT-8080}"
ADDRESS=$(echo $ADDRESS | sed s/:80$//; )

# Create a local/environment.json file. Use jq on some of
# the inputs to guarantee valid JSON encoding of strings.
cat > local/environment.json << EOF;
{ 
	"debug": ${DEBUG-false},
	"host": $(echo ${ADDRESS} | jq -R .),
	"https": ${HTTPS-false},
	"single-organization": "main",
	"static": "/tmp/static_root",
	"db": $(echo ${DBURL} | jq -R .)
}
EOF

# Add email parameters.
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
# every time the container starts if the AppSource
# fixture has been loaded.
mkdir -p /mnt/apps

# Flatten static files.
python manage.py collectstatic --noinput

# Initialize the database.
python manage.py migrate
python manage.py load_modules

# Create an initial administrative user and organization
# non-interactively and write the administrator's initial
# password to standard output.
if [ ! -z "$FIRST_RUN" ]; then
	python manage.py first_run --non-interactive
fi

# Write a file that indicates to the host that Q
# is now fully configured.
echo "done" > ready

# Start the server. The port is fixed --- see docker_container_run.sh.
python manage.py runserver 0.0.0.0:8000
