#!/bin/bash

set -euo pipefail

VENDOR=siteapp/static/vendor

SHACMD="sha256sum"
SHACMD_CHECK="$SHACMD --strict --check"
if ! command -v sha256sum > /dev/null 2>&1 ; then
  # On macOS, sha256sum is not available. Use `shasum -a 256` instead.
  # But shasum doesn't support --strict and uses --warn instead.
  SHACMD="shasum -a 256"
  SHACMD_CHECK="$SHACMD --warn --check"
fi

function download {
  # Downloads a file from the web and checks that it matches
  # a provided hash. If the comparison fails, exit immediately.
  # Usage: download https://path/to/file /tmp/save-as.tgz ABCEDF12345_THE_HASH
  URL=$1
  DEST=$2
  HASH=$3
  CHECKSUM="$HASH  $DEST"
  rm -f $DEST

  echo $URL...
  curl -# -L -o $DEST $URL
  echo

  if ! echo "$CHECKSUM" | $SHACMD_CHECK > /dev/null; then
    echo "------------------------------------------------------------"
    echo "Download of $URL did not match expected checksum."
    echo "Found:"
    $SHACMD $DEST
    echo
    echo "Expected:"
    echo "$CHECKSUM"
    rm -f $DEST
    exit 1
  fi
}


# Clear any existing vendor resources.
rm -rf $VENDOR

# Create the directory.
mkdir -p $VENDOR

# Fetch resources.

# sqlite3 3.8.3 (Public Domain)
# Django 2.2 requires SQLite 3.8.3 or later; on CentOS 7 an upgrade is needed
# We borrow the package from Fedora Project, https://koji.fedoraproject.org/koji/packageinfo?packageID=485
if command -v rpm > /dev/null 2>&1 ; then
  if test $(rpm --eval %{centos_ver}) = 7; then
    echo "Upgrading SQLite to 3.8.3"
    download \
      https://kojipkgs.fedoraproject.org/packages/sqlite/3.8.3/1.fc20/x86_64/sqlite-3.8.3-1.fc20.x86_64.rpm \
      /tmp/sqlite-3.8.3-1.fc20.x86_64.rpm \
      '4c976fc17e3676ce76aa71ce604be6d16cef36c73515e9bf1ebcdbdc6cc6e7d4'
    yum -y install /tmp/sqlite-3.8.3-1.fc20.x86_64.rpm
    rm -f /tmp/sqlite-3.8.3-1.fc20.x86_64.rpm
  fi
fi

# jQuery (MIT License)
download \
  https://code.jquery.com/jquery-3.4.1.min.js \
  $VENDOR/jquery.js \
  '0925e8ad7bd971391a8b1e98be8e87a6971919eb5b60c196485941c3c1df089a'

# Bootstrap (MIT License)
download \
  https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip \
  /tmp/bootstrap.zip \
  'f498a8ff2dd007e29c2074f5e4b01a9a01775c3ff3aeaf6906ea503bc5791b7b'
unzip -d /tmp /tmp/bootstrap.zip
mv /tmp/bootstrap-3.3.7-dist $VENDOR/bootstrap
rm -f /tmp/bootstrap.zip

# jsGrid (MIT License)
download \
  https://github.com/tabalinas/jsgrid/releases/download/v1.5.3/jsgrid-1.5.3.zip \
  /tmp/jsgrid-1.5.3.zip \
  '96ffe3ca777f6eec504af3bbc0d30951f8ebfdba8fac7cd52b42b3dbd5d54eef'
unzip -d /tmp/jsgrid /tmp/jsgrid-1.5.3.zip
mv /tmp/jsgrid $VENDOR/jsgrid
rm -f /tmp/jsgrid-1.5.3.zip

# Font Awesome (for the spinner on ajax calls, various icons; MIT License)
download \
  https://use.fontawesome.com/releases/v5.0.12/js/all.js \
  $VENDOR/fontawesome.js \
  '4f59f47836471cf3f02edfb217afdf107bf29cfe25c424c8c514a32712fc2ee8'

# Josh's Bootstrap Helpers (MIT License)
# When this (client side JS) is updated, you must also
# update templates/bootstrap-helpers.html, which is the
# corresponding HTML.
download \
  https://raw.githubusercontent.com/JoshData/html5-stub/b3c62ad/static/js/bootstrap-helpers.js \
  $VENDOR/bootstrap-helpers.js \
  'ee9d222656eef25ad5e7b0e960a5c363d18084ca333c910e8c81579c45ca4ba5'

# push.js (MIT License)
download \
  https://raw.githubusercontent.com/Nickersoft/push.js/9bad48df41a640baa29a19e9a6de02b4f45ddad4/push.js \
  $VENDOR/push.js \
  '88d16217819282c886700c2d2ed09ca93c4d7a857c5d4769ecb10ae61f72acf3'

# bootstrap-responsive-tabs (MIT License)
download \
  https://raw.githubusercontent.com/openam/bootstrap-responsive-tabs/052b957e72ca0d4954813809c2dba21f5afde072/js/responsive-tabs.js \
  $VENDOR/bootstrap-responsive-tabs.js \
  '686ed86b10ad84abf3c5d4900f64998ff3f2a2f8765dc2b3032f23d91548df07'

# auto resize textareas (MIT License)
download \
  https://raw.githubusercontent.com/jackmoore/autosize/4.0.2/dist/autosize.min.js \
  $VENDOR/autosize.min.js \
  '756f2ee1dbc42834e1269591c0b806ba06c04670373b6c2a05c55eae583d2cc7'

# text input autocomplete (MIT License)
download \
  https://github.com/yuku-t/textcomplete/releases/download/v0.17.1/textcomplete-0.17.1.tgz \
  /tmp/textcomplete.tgz \
  '6b189a50c9dd4ba1f27f16b275d34022dec57b0797f60c4afe6a7600f309ee35'
mkdir -p /tmp/textcomplete
tar -zx -C /tmp/textcomplete -f /tmp/textcomplete.tgz
mv /tmp/textcomplete/package/dist/*.min* $VENDOR/
rm -rf /tmp/textcomplete.tgz /tmp/textcomplete

# emojione (EmojiOne "Free License" https://github.com/emojione/emojione-assets/blob/master/LICENSE.md)
EMOJIONE_BASEURL=https://raw.githubusercontent.com/emojione/emojione-assets/3.1.2/sprites
mkdir $VENDOR/emojione
download \
  $EMOJIONE_BASEURL/emojione-sprite-24.min.css \
  $VENDOR/emojione/emojione-sprite-24.min.css \
  '9643c4f2b950f462f71ea15ffab848c949f3fe72a8a4a01e0a082f4d580ac754'
download \
  $EMOJIONE_BASEURL/emojione-sprite-24-people.png \
  $VENDOR/emojione/emojione-sprite-24-people.png \
  'f4324a31aabc175b083d4c136c6cd28fd0718f10d77519ba47525f1efee251b6'
download \
  $EMOJIONE_BASEURL/emojione-sprite-24-people\%402x.png \
  $VENDOR/emojione/emojione-sprite-24-people@2x.png \
  '031c43fb61be40004e1a2a1dc379fe7e0ade4cbf2998e10c9077950f1a58e8c5'
download \
  $EMOJIONE_BASEURL/emojione-sprite-24-objects.png \
  $VENDOR/emojione/emojione-sprite-24-objects.png \
  'b2a66a73e1a4c14a6b637a987d942c6b676c6033b365efc370fa9fc1a6fa8c8f'
download \
  $EMOJIONE_BASEURL/emojione-sprite-24-objects\%402x.png \
  $VENDOR/emojione/emojione-sprite-24-objects@2x.png \
  '40ac2aa1a1b90494431990689a69d8e114a7de27d5b8a6121fe0ce9f1f8b3e97'
download \
  $EMOJIONE_BASEURL/emojione-sprite-24-symbols.png \
  $VENDOR/emojione/emojione-sprite-24-symbols.png \
  '21f2268645db0cf8b5fae40b3c6263840558da4d9277ecac72adbf44fddbea22'
download \
  $EMOJIONE_BASEURL/emojione-sprite-24-symbols\%402x.png \
  $VENDOR/emojione/emojione-sprite-24-symbols@2x.png \
  '4a2d61983164c43c33dc9b2af772447175fee8ad236d430f385caf3b79184661'
# make empty files for other sprites because Django's ManifestStaticFilesStorage will bail during collectstatic
# if any assets mentioned in any CSS files (namely emojione-sprite-24.min.css) are not present.
for sprite in nature food activity travel flags regional diversity; do
  touch $VENDOR/emojione/emojione-sprite-24-$sprite.png $VENDOR/emojione/emojione-sprite-24-$sprite@2x.png
done

# quill rich text editor (BSD License)
download \
  https://github.com/quilljs/quill/releases/download/v1.3.6/quill.tar.gz \
  /tmp/quill.tar.gz \
  'a7e8b79ace3f620725d4fb543795a4cf0349db1202624c4b16304954745c3890'
tar -zx -C $VENDOR -f /tmp/quill.tar.gz
rm -f /tmp/quill.tar.gz

# js-yaml, for the authoring tool (MIT License)
download \
  https://raw.githubusercontent.com/nodeca/js-yaml/3.11.0/dist/js-yaml.min.js \
  $VENDOR/js-yaml.min.js \
  'd55680b958a58d88fb547b694a9dd37d4013ff7e2f64fe776d41c16a10c2f58e'

# google fonts
#  Hind: SIL Open Font License 1.1
# first download a helper (note: we're about to run a foreign script locally)
# TODO: Requires bash v4 not available on macOS.
download \
  https://raw.githubusercontent.com/neverpanic/google-font-download/ba0f7fd6de0933c8e5217fd62d3c1c08578b6ea7/google-font-download \
  /tmp/google-font-download \
  '1f9b2cefcda45d4ee5aac3ff1255770ba193c2aa0775df62a57aa90c27d47db5'
(cd $VENDOR; bash /tmp/google-font-download -f woff,woff2 -o google-fonts.css Hind:400 Hind:700 Lato:900)
rm -f /tmp/google-font-download
# generated with: $SHACMD $VENDOR/{google-fonts.css,Hind*,Lato*}
$SHACMD_CHECK << EOF
990e7373d100faee6fa7d92c1277695520e3c502f726bb28ce03d2b6d2cd3e6c  siteapp/static/vendor/google-fonts.css
6375a7ecbb77ba42e2de22c99aab9fea1fea125d6d857512360a3a555ff74161  siteapp/static/vendor/Hind_400.woff
d7a3280717b1f82f46bee459863720a03de43b16dc8097ba1b133440e5fe0edc  siteapp/static/vendor/Hind_400.woff2
a3ef4f13a191d01ecca06b8b997a666b28d4c614d6de256753fa9f4fbe15b726  siteapp/static/vendor/Hind_700.woff
e2f1a473a1649fe316dbddc5cf8f45c525d62b8373d1be395272864c0cf1e60f  siteapp/static/vendor/Hind_700.woff2
7831e273f41fef8485564286f3578d2847754db375befdb48b8ce37e1e1f3a57  siteapp/static/vendor/Lato_900.woff
7d4243c8e973ec0cfc707904891ae4e3efc03dbc8923acb9755f9a35c92269a6  siteapp/static/vendor/Lato_900.woff2
EOF
