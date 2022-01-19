#!/bin/bash

# This script flattens our Python package dependencies, starting
# with the dependencies listed in requirements.in. It overwrites
# requirements.txt with all packages we require, including those
# required by our dependencies, pinning each package to a version
# and including its hash, which guarantees complete reproducibility
# of dependencies on production systems.
#
# It also check's pyup.io's Python package vulnerability database
# at the end to ensure we don't depend on any known-vulnerable
# packages.

set -euf -o pipefail # abort script on error

# Install the latest pip-tools and pyup.io's safety tool.
pip3 install -U pip-tools safety

function run_update() {
	FILE_BASE=$1

	# Flatten out all of the dependencies of our dependencies to
	# requirements.txt.
	#
	# Specify --upgrade to ignore the package versions already listed
	# in requirements.txt and find the latest version of any packages
	# that are not pinned in requirements.in or by any of our dependencies.
	# (This is necessary for requirements_txt_checker.sh, which will
	# generate a requirements.txt file from scratch, and any unpinned
	# packages will be pinned to the latest upstream version, and if we
	# don't do the same here, the files won't match and the check will fail.)
	pip-compile --generate-hashes --allow-unsafe  --upgrade --output-file ${FILE_BASE}.txt --no-header ${FILE_BASE}.in
	# --allow-unsafe
	#   prevents errors during `pip3 install -r requirements.txt`
	#     by enabling pinning setuptools etc. dependencies
	#                   e.g., via --generate-hashes

	# Check packages for known vulnerabilities.
	safety check -r ${FILE_BASE}.txt
}

run_update requirements
run_update requirements_mysql
run_update requirements_util
