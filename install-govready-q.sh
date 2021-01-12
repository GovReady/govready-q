#!/bin/bash

# this script can be used to quickly set up a new  GovReady-Q instance
# for local testing, from a freshly-cloned repository.

# Usage:
#	$ ./install-govready-q.sh
#   $ ./install-govready-q.sh --non-interactive

# note that this script DOES NOT install libraries from a package manager,
# and does not edit /etc/hosts. those will have to be done manually

# Defaults
##########

# run the script be non-interactively?
# default is yes, run interactively
NONINTERACTIVE=

# some of these commands generate a big wall of text, so we may want visual space
# between them
SPACER="..."

# Parse command-line arguments
##############################

while [ $# -gt 0 ]; do
  case "$1" in
    --non-interactive)
      NONINTERACTIVE=1
      shift 1;;

    -v)
      VERBOSE=1
      shift 1;;

    --)
        shift
        break
        ;;
    *)
      echo "Unrecognized command line option: $1";
      exit 1;
    esac
done


# make sure we're not running in an environment with the wrong Python
# command names (Docker, for instance, has python3.6 as the command)
function check_has_command() {
	which $1 >/dev/null 2>&1
	return $?
}
if check_has_command python3 && check_has_command pip3
then
	: # we're good
else
	echo "ERROR: The commands 'python3' and 'pip3' are not available.";
	exit 1;
fi


# indicate mode
if [ $NONINTERACTIVE ];
then
	echo "Installing GovReady-Q in non-interactive mode..."
else
	echo "Installing GovReady-Q in interactive mode (default)..."
fi

# install basic requirements either in venv or as the local user
if test -f env/bin/activate
then
	source env/bin/activate;
	pip3 install -r requirements.txt;
elif [ -v VIRTUALENV_ENV ]
then
	pip3 install -r requirements.txt;
else
	pip3 install --user -r requirements.txt;
fi

echo $SPACER

# retrieve static assets
./fetch-vendor-resources.sh

# collect files into static directory
if [ $NONINTERACTIVE ];
then
    python3 manage.py collectstatic --no-input
else
    python3 manage.py collectstatic
fi

# create the local/environment.json file, if it is missing (it generally will be)
if [ ! -e local/environment.json ];
then
	echo "creating DEV environment.json file"

	# this is an easy way for us to get a random secret key
	SECRET_KEY_LINE="$(python3 manage.py | grep '"secret-key":')"

	# need to use a <<- heredoc if we want to have tabs be ignored
	cat <<- ENDJSON > local/environment.json
	{
		"debug": true,
		"host": "localhost:8000",
		"https": false,
		"organization-parent-domain": "localhost",
		$SECRET_KEY_LINE
	}
	ENDJSON
else
	echo "environment.json file already exists, proceeding"
fi


# run various DB setup scripts (schema, core data, etc.)
python3 manage.py migrate
python3 manage.py load_modules
echo $SPACER
echo $SPACER
echo $SPACER
if [ $NONINTERACTIVE ];
then
	python3 manage.py first_run --non-interactive
else
	python3 manage.py first_run
fi

echo $SPACER

# Use jq and cut to extract hostname from govready-url param in local/environment.json
# environment_json=$(<local/environment.json)
govready_url=`cat local/environment.json | jq .\"govready-url\"`
# echo "govready_url is $govready_url"
govready_host_and_port=$(echo $govready_url | cut -f2 -d\" | cut -f3 -d/)
echo "govready_host_and_port is $govready_host_and_port"


if [ $NONINTERACTIVE ];
then
	echo ""
	echo "*********************************"
	echo "* Starting GovReady-Q Server... *"
	echo "*********************************"
	echo ""
	python3 manage.py runserver "$govready_host_and_port"
else
	# prompt the user if they want to run the webserver now
	# this currently runs synchronously, in the foreground, so it needs to be the last
	# functional line of the script
	while true;
	do
		read -p "Do you want to run the GovReady-Q now, in the foreground? [y/n] " answer
		case $answer in
			[Yy]* ) python3 manage.py runserver "$govready_host_and_port"; break;;
			[Nn]* ) break;;
			* ) echo "Please answer 'yes' or 'no'";;
		esac
	done
fi
