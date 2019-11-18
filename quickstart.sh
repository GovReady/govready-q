#!/bin/bash

# this script can be used to quickly set up a new  GovReady-Q instance
# for local testing, from a freshly-cloned repository.

# note that this script DOES NOT install libraries from a package manager,
# and does not edit /etc/hosts. those will have to be done manually


# some of these commands generate a big wall of text, so we may want visual space
# between them
SPACER="..."

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


# install basic requirements either in venv or as the local user
if test -f env/bin/activate
then
	source env/bin/activate;
	pip3 install -r requirements.txt;
elif [ -v $VIRTUALENV_ENV ]
then
	pip3 install -r requirements.txt;
else 
	pip3 install --user -r requirements.txt;
fi
echo $SPACER
./fetch-vendor-resources.sh

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
python3 manage.py first_run
echo $SPACER

# prompt the user if they want to run data generation
while true;
do
	read -p "Do you want to add some simulated starting data (users, assessments)? [y/n] " answer
	case $answer in
		[Yy]* ) python3 manage.py add_data; break;;
		[Nn]* ) break;;
		* ) echo "Please answer 'yes' or 'no'";;
	esac
done

echo $SPACER

# prompt the user if they want to run the webserver now
# this currently runs synchronously, in the foreground, so it needs to be the last
# functional line of the script
while true;
do
	read -p "Do you want to run the webserver now, in the foreground? [y/n] " answer
	case $answer in
		[Yy]* ) python3 manage.py runserver; break;;
		[Nn]* ) break;;
		* ) echo "Please answer 'yes' or 'no'";;
	esac
done

echo $SPACER

echo 'Reminder: use the command `python3 manage.py runserver` to restart the webserver'
