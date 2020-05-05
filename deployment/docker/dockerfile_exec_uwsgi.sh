# This is the main entry point, i.e. process zero, of the
# Docker container.

set -euf -o pipefail # abort script on error

# Show the version immediately, which might help diagnose problems
# from console output.
echo "This is GovReady-Q."
cat VERSION

# Show filesystem information because the root filesystem might be
# read-only and other paths might be mounted with tmpfs and that's
# helpful to know for debugging.
echo
echo Filesystem information:
cat /proc/mounts | egrep -v "^proc|^cgroup| /proc| /dev| /sys"
echo

# Check that we're running as the 'application' user. Our Dockerfile
# specifies to run containers as that user. But cluster environments
# can override the start user and might do so to enforce running as
# a non-root user, so this process might have started up as the wrong
# user.
if [ "$(whoami)" != "application" ]; then
	echo "The container is running as the wrong UNIX user."
	id
	echo "Should be:"
	id application
	echo
fi

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
	| jq ".$1 = $(echo $2 | jq -R .)" \
	> /tmp/new-environment.json
	cat /tmp/new-environment.json > local/environment.json
	rm -f /tmp/new-environment.json
}

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

# Overridden branding.
if [ ! -z "${BRANDING-}" ]; then
	set_env_setting branding "$BRANDING"
fi

# Enterprise login settings.
if [ ! -z "${PROXY_AUTHENTICATION_USER_HEADER-}" ]; then
	set_env_setting '["trust-user-authentication-headers"].username' "$PROXY_AUTHENTICATION_USER_HEADER"
	set_env_setting '["trust-user-authentication-headers"].email' "$PROXY_AUTHENTICATION_EMAIL_HEADER"
fi

# PDF Generator settings.
if [ ! -z "${GR_PDF_GENERATOR-}" ]; then
	set_env_setting '["gr-pdf-generator"]' "$GR_PDF_GENERATOR"
fi

# Image Generator settings.
if [ ! -z "${GR_IMG_GENERATOR-}" ]; then
	set_env_setting '["gr-img-generator"]' "$GR_IMG_GENERATOR"
fi

# Write out the settings that indicate where we think the site is running at.
echo "Starting at ${ADDRESS} with HTTPS ${HTTPS-false}."

# Run checks.
python3.6 manage.py check --deploy

# Check if 0.9.0 upgrade has happened
DB_BEFORE_090=$(python3.6 manage.py db_before_090)
if [ $DB_BEFORE_090 = "True" ]
then
	echo "** WARNING!! **"
	echo "Launching this container will automatically upgrade your GovReady-Q deployment to version 0.9.0!"
	echo "Upgrading to version 0.9.0 will migrate your database."
	echo "Please review migration notes at https://govready-q.readthedocs.io/en/latest/migration_guide_086_090.html"
	if [ -z "${DB_BACKED_UP_DO_UPGRADE-}" ]
		then
			echo "'DB_BACKED_UP_DO_UPGRADE' environment variable not set."
			echo "To confirm you have backed up your database and deploy version 0.9.0, set the 'DB_BACKED_UP_DO_UPGRADE' environment variable to 'True' for your deployment."
			echo "Launch and deployment halted to protect your existing database."
			exit 1
		else
			echo "Confirmed 'DB_BACKED_UP_DO_UPGRADE' environment variable is set."
		fi
		if [ "${DB_BACKED_UP_DO_UPGRADE-}" != "True" ]
		then
			echo "'DB_BACKED_UP_DO_UPGRADE' environment variable not set to 'True'."
			echo "To confirm you have backed up your database and deploy version 0.9.0, set the 'DB_BACKED_UP_DO_UPGRADE' environment variable to 'True' for your deployment."
			echo "Launch and deployment halted to protect your existing database."
			exit 1
		else
			echo "Confirmed 'DB_BACKED_UP_DO_UPGRADE' environment variable is set to 'True'."
			echo "Continuing with deployment."
		fi
else
	echo "Confirmed that database is not initialized or has been migrated, and OK for version 0.9.0 migrations."
fi

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

