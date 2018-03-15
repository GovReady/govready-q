#!/bin/bash

# Checks that the requirements.txt file is in sync with
# requirements.in and that there are no known vulnerabilities,
# and that there are no updated packages.

set -euf -o pipefail # abort script on error

# You will need the latest pip-tools and pyup.io's safety tool:
# pip3 install -U pip-tools liccheck safety

# Flatten out all of the dependencies of our dependencies to
# a temporary file.
FN=$(tempfile)
pip-compile --generate-hashes --output-file $FN --no-header --no-annotate requirements.in > /dev/null

# Run some temporary patches on the final requirements.txt file that
# are not possible to automatically generate from requirements.in.
./requirements_txt_fixup.sh $FN

# The reverse-dependency metadata doesn't seem to be entirely
# accurate and changes nondeterministically? We omit it above
# with --no-annotate and remove it from a copy of our requirements.txt
# file before comparing.
FN2=$(tempfile)
cat requirements.txt \
	| python3 -c "import sys, re; print(re.sub(r'[\s\\\\]+# via .*', '', sys.stdin.read()));" \
	> $FN2

# Compare the requirements.txt in the repository to the one found by
# generating it from requirements.in.
if ! diff -B -u $FN $FN2; then
	rm $FN $FN2
	echo
	echo "requirements.txt is not in sync. Run requirements_txt_updater.sh."
	exit 1
fi
rm $FN $FN2
echo "requirements.txt is in sync with requirements.in."
echo

# Check packages for inappropriate licenses.
python3 <<EOF;
acceptable_licenses = {
	"CC0 (copyright waived)", "CC0 1.0 Universal",
	"BSD", "Simplified BSD", "BSD 3-Clause", "BSD 3", "BSD-3-Clause", "BSD-like",
	"MIT",
	"Apache 2.0", "Apache License 2.0", "Apache Software",
	"MPL-2.0",
	"BSD or Apache License, Version 2.0",
	"PSFL",
	"Standard PIL",
	"LGPL",
	"GNU Library or Lesser General Public License (LGPL)",
	"LGPLv3",
	"LGPLv3+"
}
dont_check_packages = {
}

import re
from liccheck.command_line import get_packages_info
acceptable_licenses = { item.lower() for item in acceptable_licenses }
for pkg in get_packages_info("requirements.txt"):
	license_strings = [pkg["license"]] + pkg["license_OSI_classifiers"]
	normalized_license_strings = { re.sub(" license$", "", license.strip().lower()) for license in license_strings }
	if len(normalized_license_strings & acceptable_licenses) == 0:
		print("Unknown/unapproved license for", pkg["name"] + ":", license_strings)
EOF

# Check packages for known vulnerabilities using pyup.io.
# Script exits on error.
safety check --bare -r requirements.txt
echo "No known vulnerabilities in Python dependencies."
echo

# Check installed packages for anything outdated. Unfortunately
# this scans *installed* packages, so it assumes you are working
# in a development environment that's been set up and that you
# have no other installed packages because it will report updates
# on those too.
FN=$(tempfile)
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
	echo
	echo "Some packages are out of date:"
	echo
	cat $FN
	rm $FN
	exit 1
else
	echo
	echo "All packages are up to date with latest upstream versions."
fi
rm $FN

