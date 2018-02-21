#!/bin/bash

set -euf -o pipefail # abort script on error

REQUIREMENTS_FILE=$1

# Fixup - get django-notifications-hq from a Github repo that applies
# a patch for Django 2.0 compatibility.
python3 -c "import sys, re; print(re.sub('(?<=\n)django-notifications-hq==.*(\n\s+--hash.*)+', 'https://github.com/phamk/django-notifications/archive/django-2-compatibility.zip \\\\\n    --hash=sha256:4da98487dda2ffcdc108f5d30db4552055056cecedb7e08edab616de763927ed\n    # see https://github.com/phamk/django-notifications/commit/652222d2b8b0ad9c23e61cf4880f85dc40d699d0', sys.stdin.read()), end='')" \
	< $REQUIREMENTS_FILE \
	> $REQUIREMENTS_FILE.new
mv $REQUIREMENTS_FILE.new $REQUIREMENTS_FILE
