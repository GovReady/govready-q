# This is the main entry point, i.e. process zero, of the
# Docker container.

set -euf -o pipefail # abort script on error

# What's the address (and port, if not 80) that end users
# will access the site at? If the HOST and PORT environment
# variables are set (and PORT is not 80), take the values
# from there, otherwise default to "localhost:8000".
ADDRESS="${HOST-localhost}:${PORT-8080}"
ADDRESS=$(echo $ADDRESS | sed s/:80$//; )

# Create a local/environment.json file. Use jq to
# guarantee valid JSON encoding of strings.
cat > local/environment.json << EOF;
{ 
	"debug": ${DEBUG-false},
	"host": $(echo ${ADDRESS} | jq -R .),
	"https": ${HTTPS-false},
	"secret-key": $(echo ${SECRET_KEY-} | jq -R .),
	"syslog": $(echo ${SYSLOG-} | jq -R .),
	"admins": ${ADMINS-[]},
	"static": "static_root",
	"db": $(echo ${DBURL-} | jq -R .)
}
EOF

function set_env_setting {
	# set_env_setting keypath value
	cat local/environment.json \
	| jq ".[\"$1\"] = $(echo $2 | jq -R .)" \
	> /tmp/new-environment.json
	cat /tmp/new-environment.json > local/environment.json
	rm -f /tmp/new-environment.json
}

# Add Q settings.
if [ -z "${ORGANIZATION_PARENT_DOMAIN-}" ]; then
	# Not multi-tenant with "main" as the subdomain of the
	# default organization.
	set_env_setting single-organization main
else
	# Multi-tenant.
	set_env_setting organization-parent-domain "$ORGANIZATION_PARENT_DOMAIN"
fi

# Add email parameters.
if [ ! -z "${EMAIL_HOST-}" ]; then
	set_env_setting email.host "$EMAIL_HOST"
	set_env_setting email.port "$EMAIL_PORT"
	set_env_setting email.user "$EMAIL_USER"
	set_env_setting email.pw "$EMAIL_PW"
	set_env_setting email.domain "$EMAIL_DOMAIN"
fi
if [ ! -z "${MAILGUN_API_KEY-}" ]; then
	set_env_setting mailgun_api_key "$MAILGUN_API_KEY"
fi

# Write out the settings that indicate where we think the site is running at.
echo "Starting GovReady-Q at ${ADDRESS} with HTTPS ${HTTPS-false}."

# Initialize the database.
python3.6 manage.py migrate
python3.6 manage.py load_modules

# Create an initial administrative user and organization
# non-interactively and write the administrator's initial
# password to standard output.
if [ ! -z "${FIRST_RUN-}" ]; then
	echo "Running FIRST_RUN actions..."
	python3.6 manage.py first_run --non-interactive
fi

# Configure the HTTP+applications server.
# * The port is fixed --- see docker_container_run.sh.
# * Use 4 concurrent processes by default. Expose management statistics to localhost only.
cat > /tmp/uwsgi.ini <<EOF;
[uwsgi]
http = 0.0.0.0:8000
wsgi-file = siteapp/wsgi.py
processes = ${PROCESSES-4}
stats = 127.0.0.1:9191
EOF

# Write a file that indicates to the host that Q
# is now fully configured. It will still be a few
# moments before uWSGI is accepting connections.
echo "done" > /tmp/govready-q-is-ready
echo "GovReady-Q is starting."
echo # usgi output follows

# Start the server.
exec supervisord -n

