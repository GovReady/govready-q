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

# Construct version information.
VERSION_TAG_PATTERN="v*"
if ! VERSION=$(git describe --tags --exact-match --match $VERSION_TAG_PATTERN 2> /dev/null); then
	echo "WARNING: The HEAD commit is not tagged."
	echo
	WARNINGS=1

	# Fall back to a recent tag or, if there are no tags (which should
	# never occur after right now) the current commit number.
	if ! VERSION=$(git describe --long --tags --match $VERSION_TAG_PATTERN --always); then
		echo "WARNING: Could not get a version string."
		exit 1
	fi
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
