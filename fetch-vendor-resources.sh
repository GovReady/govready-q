#!/bin/bash

set -euo pipefail

VENDOR=siteapp/static/vendor

# Clear any existing vendor resources.
rm -rf $VENDOR

# Create the directory.
mkdir -p $VENDOR

# Fetch resources.

# jQuery (MIT License)
curl -L -o $VENDOR/jquery.js \
        https://code.jquery.com/jquery-3.1.1.min.js

# Bootstrap (MIT License)
curl -L -o /tmp/bootstrap.zip \
        https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip
unzip -d /tmp /tmp/bootstrap.zip
mv /tmp/bootstrap-3.3.7-dist $VENDOR/bootstrap
rm -f /tmp/bootstrap.zip

# Font Awesome (for the spinner on ajax calls; MIT License)
curl -L -o /tmp/fontawesome.zip \
        http://fontawesome.io/assets/font-awesome-4.7.0.zip
unzip -d /tmp /tmp/fontawesome.zip
mv /tmp/font-awesome-4.7.0 $VENDOR/fontawesome
rm -f /tmp/fontawesome.zip

# Josh's Bootstrap Helpers (MIT License)
curl -L -o $VENDOR/bootstrap-helpers.js \
        https://raw.githubusercontent.com/JoshData/html5-stub/3b9b623a0969a030ca9a5657b4be9fabb9fca43d/static/js/bootstrap-helpers.js

# push.js (MIT License)
curl -L -o $VENDOR/push.js \
        https://raw.githubusercontent.com/Nickersoft/push.js/9bad48df41a640baa29a19e9a6de02b4f45ddad4/push.js

# bootstrap-responsive-tabs (MIT License)
curl -L -o $VENDOR/bootstrap-responsive-tabs.js \
        https://raw.githubusercontent.com/openam/bootstrap-responsive-tabs/052b957e72ca0d4954813809c2dba21f5afde072/js/responsive-tabs.js

# auto resize textareas (MIT License)
curl -L -o $VENDOR/autosize.min.js \
        https://raw.githubusercontent.com/jackmoore/autosize/master/dist/autosize.min.js

# text input autocomplete (MIT License)
curl -L -o $VENDOR/jquery.textcomplete.min.js \
        https://raw.githubusercontent.com/yuku-t/jquery-textcomplete/master/dist/jquery.textcomplete.min.js

# emojione (Creative Commons Attribution 4.0 International & MIT License)
curl -L -o $VENDOR/emojione.min.css \
        https://raw.githubusercontent.com/Ranks/emojione/v2.2.7/assets/css/emojione.min.css
curl -L -o $VENDOR/emojione.min.js \
        https://raw.githubusercontent.com/Ranks/emojione/v2.2.7/lib/js/emojione.min.js

# quill rich text editor (BSD License)
curl -L -o /tmp/quill.tar.gz \
        https://github.com/quilljs/quill/releases/download/v1.2.5/quill.tar.gz
tar -zx -C $VENDOR -f /tmp/quill.tar.gz
rm -f /tmp/quill.tar.gz

# js-yaml, for the authoring tool (MIT License)
curl -L -o $VENDOR/js-yaml.min.js \
        https://raw.githubusercontent.com/nodeca/js-yaml/3.9.1/dist/js-yaml.min.js

# google fonts
#  Hind: SIL Open Font License 1.1
# first download a helper (note: we're about to run a foreign script locally)
# TODO: Requires bash v4 not available on macOS.
curl -L -o /tmp/google-font-download \
        https://raw.githubusercontent.com/neverpanic/google-font-download/master/google-font-download
(cd $VENDOR; bash /tmp/google-font-download -f woff,woff2 -o google-fonts.css Hind:400 Hind:700 Lato:900)
rm -f /tmp/google-font-download
