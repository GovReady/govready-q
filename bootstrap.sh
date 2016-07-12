# Deployment assuming only appserver, no webserver here.

set -x

stuff() {
  # Update the cache of available packages
  apt-get update

  # Uncomment the next line if you actually need to upgrade packages
  #[ $? == 0 ] && apt-get upgrade -y

  apt-get install -y git python3-pip unzip
  pip3 install -U pip  # get pip8 or so to work with git+https
}

set -x
vagrant=/tmp/vagrant$RANDOM
echo SENDING TO $vagrant

cat<<ENDV>$vagrant
#!/bin/bash -x
  cd /home/vagrant
  mkdir -p .ssh
  chmod 0700 .ssh
  cat <<ENDCONF>.ssh/config
Host github.com
  IdentityFile /home/vagrant/.ssh/govreadydeploykey
  StrictHostKeyChecking No
ENDCONF
  cat<<ENDKEY>.ssh/govreadydeploykey
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
ENDKEY

  # use deploykey to get the private repository
  chmod 0400 /home/vagrant/.ssh/govreadydeploykey
  git clone git@github.com:pburkholder/govready-q.git

  cd govready-q
  # This is for CF deploy, not needed yet
  #mkdir -p vendor
  #pip install --download vendor -r requirements.txt

  pip install --user -r requirements.txt

  deployment/fetch-vendor-resources.sh

  cat <<ENDJ>/home/vagrant/govready-q/local/environment.json
  {
    "debug": true,
    "host": "localhost:8000",
    "https": false,
    "secret-key": "@-uks6_6r$e6qp2*7irerq5%l2a8vbtxv#fd4nfjyd%(fz85x4",
    "govready_cms_api_auth": null
  }
ENDJ
  python3 manage.py migrate
  python3 manage.py load_modules
  python3 manage.py runserver
ENDV

stuff
chmod 755 $vagrant
/usr/bin/sudo -u vagrant $vagrant
