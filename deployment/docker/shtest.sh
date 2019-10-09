set -euf -o pipefail # abort script on error

# Show the version immediately, which might help diagnose problems
# from console output.
echo "This is GovReady-Q."
cat VERSION
echo "\n"

# Show filesystem information because the root filesystem might be
# read-only and other paths might be mounted with tmpfs and that's
# helpful to know for debugging.
# echo
# echo Filesystem information:
# cat /proc/mounts | egrep -v "^proc|^cgroup| /proc| /dev| /sys"
# echo



# Check if 0.9.0 upgrade has happened
DB_BEFORE_090=$(python3 manage.py db_before_090)
if [ $DB_BEFORE_090 != "True" ]
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
	echo "Confirmed upgrade to version 0.9.0 previously completed."
fi

echo "Continuining script"