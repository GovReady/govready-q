#!/bin/bash

# Checks that the requirements.txt file is in sync with
# requirements.in and that there are no known vulnerabilities,
# and that there are no updated packages.
#
# Usage
#   $ ./requirements_txt_checker.sh
#

set -euf -o pipefail # abort script on error

# You will need the latest pip-tools and pyup.io's safety tool:
# pip3 install -U pip-tools safety

# Flatten out all of the dependencies of our dependencies to
# a temporary file.
FN=$(mktemp)
echo "Flattening transitive dependencies to a temporary file $FN"
pip-compile --generate-hashes --output-file $FN --no-header --no-annotate requirements.in > /dev/null

# The reverse-dependency metadata doesn't seem to be entirely
# accurate and changes nondeterministically? We omit it above
# with --no-annotate and remove it from a copy of our requirements.txt
# file before comparing.
# FN2=$(tempfile)
FN2=$(mktemp)
echo "Clean up of temporary requirements file for comparisons"
cat requirements.txt \
	| python3 -c "import sys, re; print(re.sub(r'[\s\\\\]+# via .*', '', sys.stdin.read()));" \
	> $FN2

# Compare the requirements.txt in the repository to the one found by
# generating it from requirements.in.
echo "Comparing requirements.txt to temporary generated version from requirements.in"
if ! diff -B -u $FN $FN2; then
	echo
	echo "requirements.txt is not in sync with requirements.in. Some packages may have updates available. Run requirements_txt_updater.sh."
else
	echo "requirements.txt is in sync with requirements.in."
fi

rm $FN $FN2
echo

# Check installed packages for anything outdated. Unfortunately
# this scans *installed* packages, so it assumes you are working
# in a development environment that's been set up and that you
# have no other installed packages because it will report updates
# on those too.
echo "Check installed packages for anything outdated"
FN=$(mktemp)
pip3 list --outdated --format=columns > $FN

if [ -f requirements_txt_checker_ignoreupdates.txt ]; then
	# Some updates we ignore. Those are listed in requirements_txt_checker_ignoreupdates.txt
	# in a format similar to a requirements.txt, each line like:
	# pagename==version
	# For each line, remove that line from the `pip list --outdated` output.
	for PKG_EQ_VER in $(cat requirements_txt_checker_ignoreupdates.txt); do
		PKG_VER=(${PKG_EQ_VER//==/ }) # split on ==, make a bash array
		echo "Ignoring new ${PKG_VER[0]} version ${PKG_VER[1]}."
		grep "^${PKG_VER[0]}  *[^ ][^ ]*  *${PKG_VER[1]} " $FN || /bin/true
		sed -i "/^${PKG_VER[0]}  *[^ ][^ ]*  *${PKG_VER[1]} /d" $FN
	done
fi

if [ $(cat $FN | wc -l) -gt 2 ]; then
	echo "Some packages are out of date:"
	echo
	cat $FN
else
	echo "All packages are up to date with latest upstream versions."
fi
rm $FN
