#!/bin/bash

set -euo pipefail

VENDOR=siteapp/static/vendor

SHACMD="sha256sum --strict"
if ! which sha256sum > /dev/null; then
  # On macOS, sha256sum is not available. Use `shasum -a 256` instead.
  # But shasum doesn't support --strict and uses --warn instead.
  SHACMD="shasum -a 256 --warn"
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

  if ! echo "$CHECKSUM" | $SHACMD --check > /dev/null; then
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

# jQuery (MIT License)
download \
  https://code.jquery.com/jquery-3.1.1.min.js \
  $VENDOR/jquery.js \
  '85556761a8800d14ced8fcd41a6b8b26bf012d44a318866c0d81a62092efd9bf'

# Bootstrap (MIT License)
download \
  https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip \
  /tmp/bootstrap.zip \
  'f498a8ff2dd007e29c2074f5e4b01a9a01775c3ff3aeaf6906ea503bc5791b7b'
unzip -d /tmp /tmp/bootstrap.zip
mv /tmp/bootstrap-3.3.7-dist $VENDOR/bootstrap
rm -f /tmp/bootstrap.zip

# Font Awesome (for the spinner on ajax calls; MIT License)
download \
  http://fontawesome.io/assets/font-awesome-4.7.0.zip \
  /tmp/fontawesome.zip \
  'a7b6edb9e874e6d36a90160553afeb412f85df4d91c723ef2a29a2b5bf8e5802'
unzip -d /tmp /tmp/fontawesome.zip
mv /tmp/font-awesome-4.7.0 $VENDOR/fontawesome
rm -f /tmp/fontawesome.zip

# Josh's Bootstrap Helpers (MIT License)
download \
  https://raw.githubusercontent.com/JoshData/html5-stub/3b9b623a0969a030ca9a5657b4be9fabb9fca43d/static/js/bootstrap-helpers.js \
  $VENDOR/bootstrap-helpers.js \
  '65214acdd7f4fa41c78634999b1f3385c918787f59beb66bba2770e709877a41'

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
  https://raw.githubusercontent.com/jackmoore/autosize/master/dist/autosize.min.js \
  $VENDOR/autosize.min.js \
  '17b05b73ede11afdf80fea1bb071ec4a6dd929106e75647b7b61f47d2d1b7a89'

# text input autocomplete (MIT License)
download \
  https://raw.githubusercontent.com/yuku-t/jquery-textcomplete/master/dist/jquery.textcomplete.min.js \
  $VENDOR/jquery.textcomplete.min.js \
  '8936cb4a0e36ec66e03c21883f0d0f18b404cd4cdf51c82167d926a084b0db51'

# emojione (Creative Commons Attribution 4.0 International & MIT License)
download \
  https://raw.githubusercontent.com/Ranks/emojione/v2.2.7/assets/css/emojione.min.css \
  $VENDOR/emojione.min.css \
  '519edf0dc00972d9a811c5e60b94cf719b30351a8dfe62f38fab8d4b5182558b'
download \
  https://raw.githubusercontent.com/Ranks/emojione/v2.2.7/lib/js/emojione.min.js \
  $VENDOR/emojione.min.js \
  'f5c06455e539dcd889f7f05d709b5adc76c444099fe57f431365af2fc57e803b'

# quill rich text editor (BSD License)
download \
  https://github.com/quilljs/quill/releases/download/v1.2.5/quill.tar.gz \
  /tmp/quill.tar.gz \
  '9f1756d90c6330b2d91209bbc7634ca32916f2388387b1e93cbf11655dfeff6b'
tar -zx -C $VENDOR -f /tmp/quill.tar.gz
rm -f /tmp/quill.tar.gz

# js-yaml, for the authoring tool (MIT License)
download \
  https://raw.githubusercontent.com/nodeca/js-yaml/3.9.1/dist/js-yaml.min.js \
  $VENDOR/js-yaml.min.js \
  'fb3094718fec03e5a536355b69c57b6abae6d3306dda168841405bc0d28437b9'

# google fonts
#  Hind: SIL Open Font License 1.1
# first download a helper (note: we're about to run a foreign script locally)
# TODO: Requires bash v4 not available on macOS.
download \
  https://raw.githubusercontent.com/neverpanic/google-font-download/master/google-font-download \
  /tmp/google-font-download \
  'a59054f45e738118f7a164527c4fa71ed42050aaeff2c21b75ab5b5512257a2a'
(cd $VENDOR; bash /tmp/google-font-download -f woff,woff2 -o google-fonts.css Hind:400 Hind:700 Lato:900)
rm -f /tmp/google-font-download
# generated with: $SHACMD $VENDOR/{google-fonts.css,Hind*,Lato*}
$SHACMD --check << EOF
d9ae96839e4668eb006885ec9f1d51dde2553d2cf53437ff9b8963c0e583ec69  siteapp/static/vendor/google-fonts.css
f0609555ad20470e30de0ba32d026f0b27098ea74c84edd811e21998943510f6  siteapp/static/vendor/Hind_400.woff
af6e56a25aae4ec8eaa3aac31a8a73c0d1aaa4c4dd6afbee4f1c996474fcd789  siteapp/static/vendor/Hind_400.woff2
53beffe7dff224394b4f0e1f681ba3a64591c63e882720071863b4f5b8572bdf  siteapp/static/vendor/Hind_700.woff
f43a318a03ccb1c5f135ceca9ca3209f2acdc98ade18500dec807b6b1703e68f  siteapp/static/vendor/Hind_700.woff2
2a6deb3135f92894e02fc63f6faa395e639fd44bfb3e7664608746715cd21bb7  siteapp/static/vendor/Lato_900.woff
abde463ef27458713d91e9be883fdd389298ef57411b601cab5f66db609c508d  siteapp/static/vendor/Lato_900.woff2
EOF