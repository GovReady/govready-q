#!/bin/bash

set -euf -o pipefail # abort script on error

WARNINGS=0

# TODO: Take an argument to build with Gunicorn instead of the default uWSGI.

if [ ! -f Dockerfile ]; then
	echo "This should be run from the root of the GovReady-Q repository."
	exit 1
fi

# Check that there are no uncommitted changes.
if ! git diff-index --quiet HEAD --; then
    echo "WARNING: There are uncommitted changes."
	echo
	WARNINGS=1

# Check that the HEAD commit is pushed.
elif ! git branch -r --contains | grep "^\s*origin/master$" > /dev/null; then
	echo "WARNING: Your branch is ahead of origin/master. Push first."
	echo
	WARNINGS=1
fi

# Determine the version from any tag of the HEAD commit
# that starts with "v".
VERSION_TAG_PATTERN="v*"
if VERSION=$(git describe --tags --exact-match --match $VERSION_TAG_PATTERN 2> /dev/null); then
	# The tag must match the first line of the VERSION file.
	VERSION2=$(cat VERSION | head -1)
	if [[ "$VERSION" != "$VERSION2" ]]; then
		echo "ERROR: The version tag $VERSION does not match the version $VERSION2 stored in the VERSION file."
		exit 1
	fi

	# Check that the tag has a CHANGELOG entry.
	if ! grep "^$VERSION " CHANGELOG.md > /dev/null; then
		echo "ERROR: There is no CHANGELOG.md entry for $VERSION."
		exit 1
	fi

	# Validate that the tag is pushed (check that it exists on
	# origin and refers to the same commit and, if applicable,
	# has same annotated tag content).
	LOCAL_TAG=$(git rev-parse $VERSION)
	REMOTE_TAG=$(git ls-remote --tags origin $VERSION)
	if [ "$REMOTE_TAG" != "$LOCAL_TAG	refs/tags/$VERSION" ]; then
		echo "ERROR: The tag $VERSION is not present on origin or is different from the local tag. Run \`git push origin $VERSION\` first."
		exit 1
	fi

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

# Update the local copy of the base image so we are building against
# the latest upstream base.
BASEIMAGE=$(grep ^FROM Dockerfile | sed "s/FROM //")
echo "Updating $BASEIMAGE..."
docker image pull $BASEIMAGE

# Write a VERSION file to go into the image.
cat > VERSION << EOF;
$VERSION
$COMMIT
EOF

echo "Building version:"
cat VERSION
echo

# Build the image.
docker image build --tag govready/govready-q:$VERSION .

# Show push commands.
echo
echo "To publish, run:"
echo "docker image push govready/govready-q:$VERSION"
echo "docker image tag govready/govready-q:$VERSION govready/govready-q:latest && docker image push govready/govready-q:latest"

# Show warning again.
if [ $WARNINGS -gt 0 ]; then
	echo
	echo "WARNING: There were warnings --- see above."
	exit 1
fi
