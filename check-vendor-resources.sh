#!/bin/bash

set -euo pipefail

# retrieve 'static' from local/environment.json
if [ -f local/environment.json ] ; then
  VENDOR=$(python3 -c "import json; f=open('local/environment.json', 'r'); env=json.load(f); print(env.get('static',''))")
fi

# if VENDOR not set above, use default
if [ -z "$VENDOR" ] ; then
  VENDOR=siteapp/static/vendor
fi

SHACMD="sha256sum"
SHACMD_CHECK="$SHACMD --strict --check"
if ! command -v sha256sum > /dev/null 2>&1 ; then
  # On macOS, sha256sum is not available. Use `shasum -a 256` instead.
  # But shasum doesn't support --strict and uses --warn instead.
  SHACMD="shasum -a 256"
  SHACMD_CHECK="$SHACMD --warn --check"
fi

# generated with: $SHACMD `find $VENDOR -type f | sort -f`
$SHACMD_CHECK << EOF
756f2ee1dbc42834e1269591c0b806ba06c04670373b6c2a05c55eae583d2cc7  siteapp/static/vendor/autosize.min.js
ee9d222656eef25ad5e7b0e960a5c363d18084ca333c910e8c81579c45ca4ba5  siteapp/static/vendor/bootstrap-helpers.js
686ed86b10ad84abf3c5d4900f64998ff3f2a2f8765dc2b3032f23d91548df07  siteapp/static/vendor/bootstrap-responsive-tabs.js
c4ea52f9efdd111f33ef6c3eaabc8289e386cac408f1c10b015b773071b4a616  siteapp/static/vendor/bootstrap/css/bootstrap-theme.css
71941b253b8942374cd57b8a85d473489f21311438ba9e3dd4fefa22adbf0f53  siteapp/static/vendor/bootstrap/css/bootstrap-theme.css.map
653e073e97423adda5bc3917a241ee8497dd38a48f14bcde0098a4e54fd0fa5e  siteapp/static/vendor/bootstrap/css/bootstrap-theme.min.css
9851e169f044bfc0d5e4a8a761ded531d415ceb7febc1ea585fab070b846d738  siteapp/static/vendor/bootstrap/css/bootstrap-theme.min.css.map
7e630d90c7234b0df1729f62b8f9e4bbfaf293d91a5a0ac46df25f2a6759e39a  siteapp/static/vendor/bootstrap/css/bootstrap.css
9cd84a2a5162c816a8bbbd79cf9dc0605bc0ea86e4cd2bab43aee069bb83d266  siteapp/static/vendor/bootstrap/css/bootstrap.css.map
f75e846cc83bd11432f4b1e21a45f31bc85283d11d372f7b19accd1bf6a2635c  siteapp/static/vendor/bootstrap/css/bootstrap.min.css
b4a35d19793de445f4622f4d28db279c0242b60228ef304340aad833d012a77d  siteapp/static/vendor/bootstrap/css/bootstrap.min.css.map
13634da87d9e23f8c3ed9108ce1724d183a39ad072e73e1b3d8cbf646d2d0407  siteapp/static/vendor/bootstrap/fonts/glyphicons-halflings-regular.eot
42f60659d265c1a3c30f9fa42abcbb56bd4a53af4d83d316d6dd7a36903c43e5  siteapp/static/vendor/bootstrap/fonts/glyphicons-halflings-regular.svg
e395044093757d82afcb138957d06a1ea9361bdcf0b442d06a18a8051af57456  siteapp/static/vendor/bootstrap/fonts/glyphicons-halflings-regular.ttf
a26394f7ede100ca118eff2eda08596275a9839b959c226e15439557a5a80742  siteapp/static/vendor/bootstrap/fonts/glyphicons-halflings-regular.woff
fe185d11a49676890d47bb783312a0cda5a44c4039214094e7957b4c040ef11c  siteapp/static/vendor/bootstrap/fonts/glyphicons-halflings-regular.woff2
0abe8deb334de1ba743b04d0399e99eba336afed9da72fc4c0a302c99f9238c8  siteapp/static/vendor/bootstrap/js/bootstrap.js
53964478a7c634e8dad34ecc303dd8048d00dce4993906de1bacf67f663486ef  siteapp/static/vendor/bootstrap/js/bootstrap.min.js
c7aa82a1aa7d45224a38d926d2adaff7fe4aef5bcdafa2a47bdac057f4422c2d  siteapp/static/vendor/bootstrap/js/npm.js
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-activity.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-activity@2x.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-diversity.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-diversity@2x.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-flags.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-flags@2x.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-food.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-food@2x.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-nature.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-nature@2x.png
b2a66a73e1a4c14a6b637a987d942c6b676c6033b365efc370fa9fc1a6fa8c8f  siteapp/static/vendor/emojione/emojione-sprite-24-objects.png
40ac2aa1a1b90494431990689a69d8e114a7de27d5b8a6121fe0ce9f1f8b3e97  siteapp/static/vendor/emojione/emojione-sprite-24-objects@2x.png
f4324a31aabc175b083d4c136c6cd28fd0718f10d77519ba47525f1efee251b6  siteapp/static/vendor/emojione/emojione-sprite-24-people.png
031c43fb61be40004e1a2a1dc379fe7e0ade4cbf2998e10c9077950f1a58e8c5  siteapp/static/vendor/emojione/emojione-sprite-24-people@2x.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-regional.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-regional@2x.png
21f2268645db0cf8b5fae40b3c6263840558da4d9277ecac72adbf44fddbea22  siteapp/static/vendor/emojione/emojione-sprite-24-symbols.png
4a2d61983164c43c33dc9b2af772447175fee8ad236d430f385caf3b79184661  siteapp/static/vendor/emojione/emojione-sprite-24-symbols@2x.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-travel.png
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  siteapp/static/vendor/emojione/emojione-sprite-24-travel@2x.png
9643c4f2b950f462f71ea15ffab848c949f3fe72a8a4a01e0a082f4d580ac754  siteapp/static/vendor/emojione/emojione-sprite-24.min.css
4f59f47836471cf3f02edfb217afdf107bf29cfe25c424c8c514a32712fc2ee8  siteapp/static/vendor/fontawesome.js
990e7373d100faee6fa7d92c1277695520e3c502f726bb28ce03d2b6d2cd3e6c  siteapp/static/vendor/google-fonts.css
6375a7ecbb77ba42e2de22c99aab9fea1fea125d6d857512360a3a555ff74161  siteapp/static/vendor/Hind_400.woff
d7a3280717b1f82f46bee459863720a03de43b16dc8097ba1b133440e5fe0edc  siteapp/static/vendor/Hind_400.woff2
a3ef4f13a191d01ecca06b8b997a666b28d4c614d6de256753fa9f4fbe15b726  siteapp/static/vendor/Hind_700.woff
e2f1a473a1649fe316dbddc5cf8f45c525d62b8373d1be395272864c0cf1e60f  siteapp/static/vendor/Hind_700.woff2
160a426ff2894252cd7cebbdd6d6b7da8fcd319c65b70468f10b6690c45d02ef  siteapp/static/vendor/jquery.js
d55680b958a58d88fb547b694a9dd37d4013ff7e2f64fe776d41c16a10c2f58e  siteapp/static/vendor/js-yaml.min.js
7831e273f41fef8485564286f3578d2847754db375befdb48b8ce37e1e1f3a57  siteapp/static/vendor/Lato_900.woff
7d4243c8e973ec0cfc707904891ae4e3efc03dbc8923acb9755f9a35c92269a6  siteapp/static/vendor/Lato_900.woff2
88d16217819282c886700c2d2ed09ca93c4d7a857c5d4769ecb10ae61f72acf3  siteapp/static/vendor/push.js
3a1b43d7e6f821bc71dfad562ccc91fa5b25e7235d16705239a2b13c2165079f  siteapp/static/vendor/quill/examples/bubble.html
2bb9bf4545854970d4e43e70b0a82ba3bdc0fc5c8965a215a56452c3446324f8  siteapp/static/vendor/quill/examples/full.html
201a6f13117c2653ab1c06efa2ab702a05d876775d5963548b746b6c5494715e  siteapp/static/vendor/quill/examples/snow.html
48b1b42379c43ddbbf6ca013334f983068a10a62f6d223432a166872ec0ec0e9  siteapp/static/vendor/quill/quill.bubble.css
b6235e6b05b8c5d649479fe9f6113622410930ced252e5fceeea53caa3eab7d9  siteapp/static/vendor/quill/quill.core.css
f7089de1eb6ecb869a800a144a38e59c0a7349bf76a655a316af7645161b1531  siteapp/static/vendor/quill/quill.core.js
a4da70cd71b5a0e224e95865829a8356a93907c7d47ebb6b23cb8014c6ff9c48  siteapp/static/vendor/quill/quill.js
de86018869b5e845bdc101fc1b55611a1e375e08af6cee4a681d7446103da611  siteapp/static/vendor/quill/quill.min.js
be1d65da4425b26396c70033141dcbb88d8304738ae67d8625b9920e3b74b02b  siteapp/static/vendor/quill/quill.min.js.map
892e299431955e9ae388ae257f72024ee76af2d52a7a97a868f70fbe50f16144  siteapp/static/vendor/quill/quill.snow.css
478b4685b0dd8fd1a7a6455714304b30234e39013c77c0c94a35fcf19e307178  siteapp/static/vendor/textcomplete.min.js
910673bac3223d8e8b8b8380882cc51b26d1727c199b013acc35eca65df7d7a5  siteapp/static/vendor/textcomplete.min.js.map
EOF
