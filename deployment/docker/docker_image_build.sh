#!/bin/bash

set -euf -o pipefail # abort script on error

WARNINGS=0

if [ ! -f Dockerfile ]; then
	echo "This should be run from the root of the GovReady-Q repository."
	exit 1
fi

# Check that there are no uncommitted changes.
if ! git diff-index --quiet HEAD --; then
    echo "There are uncommitted changes. Commit first."
    exit 1
fi

# Check that the HEAD commit is pushed.
if ! git branch -r --contains | grep "^\s*origin/master$" > /dev/null; then
	echo "WARNING: Your branch is ahead of origin/master. Push first?"
	echo
	WARNINGS=1
fi

# Determine the version from any tag of the HEAD commit
# that starts with "v".
VERSION_TAG_PATTERN="v*"
if VERSION=$(git describe --tags --exact-match --match $VERSION_TAG_PATTERN 2> /dev/null); then
	# Validate that the tag is a PEP440 "public version number",
	# which is in the form N(.N)*[{a|b|rc}N][.postN][.devN].
	python3 - "$VERSION" <<EOF;
import sys
from pkg_resources import parse_version, SetuptoolsVersion
v = parse_version(sys.argv[1])
if not isinstance(v, SetuptoolsVersion) or v.local:
	print("ERROR: The version number {} is not a PEP440-compliant public version number.".format(repr(sys.argv[1])))
	sys.exit(1)
EOF

else
	# During development, we may be testing a build that
	# is not yet tagged. In that case, pull the version
	# number from `git describe` which gives a string
	# composed of a recent tag, the number of commits
	# that have occurred since that tag, and then a short
	# hash of the current commit. It won't be PEP440-compliant.
	if ! VERSION=$(git describe --long --tags --match $VERSION_TAG_PATTERN --always); then
		echo "WARNING: Could not get a version string. There is no recent tag in the pattern '$VERSION_TAG_PATTERN'."
		exit 1
	fi

	echo "WARNING: The HEAD commit is not tagged. Using \`git describe\` instead."
	echo
	WARNINGS=1
fi

# Append the current commit hash as the second line of the VERSION file.
COMMIT=$(git rev-parse HEAD)

cat > VERSION << EOF;
$VERSION
$COMMIT
EOF

echo "Building version:"
cat VERSION
echo

# Build the image.
docker image build --tag govready/govready-q:${TAG-latest} .
rm -f VERSION # it's for Docker only

# Show warning again.
if [ $WARNINGS -gt 0 ]; then
	echo
	echo "WARNING: There were warnings --- see above."
	exit 1
fi
