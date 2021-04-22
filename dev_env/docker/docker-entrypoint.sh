#!/bin/bash

mkdir -p local

echo "[ + ] Setting up SSH for remote Interpreter use"
if [[ ! -d /usr/src/app/dev_env/docker/ssh ]]; then
    echo "Configuring SSH Daemon"
    mkdir -p /usr/src/app/dev_env/docker/ssh
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
    ssh-keygen -A
    chmod -R 400 /etc/ssh
    cp /etc/ssh /usr/src/app/dev_env/docker -r
fi
/usr/sbin/sshd
export -p > /usr/src/app/dev_env/docker/remote_interpreter/env_var.sh

ln -sf /usr/src/app/dev_env/docker/environment.json /usr/src/app/local/environment.json

echo "[ + ] Running checks"
pip3 install -r requirements.txt --ignore-installed

echo "[ + ] Running checks"
./manage.py check --deploy

echo "[ + ] Migrating Database"
./manage.py migrate


if [[ ! -f "/usr/src/app/local/first_run.lock" ]]; then
    echo "[ + ] Preparing Data"
    ./manage.py load_modules
    ./manage.py first_run --non-interactive

    echo "[ + ] Setting up GovReady-Q sample project if none exists"
    ./manage.py load_govready_ssp

    touch /usr/src/app/local/first_run.lock
fi

echo "[ + ] Starting server"
./manage.py runserver 0.0.0.0:8000
