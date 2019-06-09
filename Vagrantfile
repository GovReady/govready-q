# -*- mode: ruby -*-
# vi: set ft=ruby :
#
# This file is based on our CentOS 7 installation instructions at docs/source/deploy_rhel7_centos7.md
# (also at https://govready-q.readthedocs.io/en/latest/deploy_rhel7_centos7.html). See that file for
# details and *please* keep the steps in this file in sync with the steps in the documentation.
# The setup here differs from the documentation in the following ways:
# * Rather than creating a govready-q UNIX user, we use the default 'vagrant' user.
# * We don't need to clone the Q source code because the Q root directory is already mounted at /vagrant.
# * Python packages are installed by pip at the system level rather than with --user since this machine is expected to be easily thrown away (I guess we could 'sudo -u vagrant).
# * We configure Q with using 'jq' to construct the file, setting the hostname to the IP address of the VM.
# * We turn debug mode off, and consequently must specify a static path and run collectstatic to serve static assets.
# * We copy & edit the supervisord config because the paths are different.
#
# Usage:
# git clone https://github.com/govready/govready-q
# cd govready-q
# git checkout {choose the tag for the current released version}
# vagrant up
# vagrant ssh -- -t manage first_run                     (note that the -t creates a TTY for interactive input)
# visit http://192.168.150.150:3031/ in your browser!
#
Vagrant.configure(2) do |config|
  config.vm.box = "centos/7"

  config.vm.network "private_network", ip: "192.168.150.150"
  config.vm.provision "shell", inline: <<-SHELL
    # Install system packages and upgrade pip.
    rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm https://rhel7.iuscommunity.org/ius-release.rpm
    yum install -y git2u jq
    yum install -y --disablerepo=ius \
        unzip gcc python34-pip python34-devel \
        graphviz \
        pandoc xorg-x11-server-Xvfb wkhtmltopdf \
        postgresql mysql-devel
    pip3 install --upgrade pip

    # Install Python packages and fetch other dependencies.
    cd /vagrant # Q source code directory
    pip3 install -r requirements.txt
    ./fetch-vendor-resources.sh # note - this overwrites host files in siteapp/static/vendor, but that's ok

    # Write a local/environment.json file. Skip if the file is already present
    # because this is mounted to a host directory and we don't want to clobber
    # a file on the host.
    if [ ! -f local/environment.json ]; then
        mkdir -p local
        echo '{}' \
          | jq '.["debug"]=false' \
          | jq '.["https"]=false' \
          | jq '.["host"]="192.168.150.150:3031"' \
          | jq '.["static"]="/tmp/public_html_static"' \
          > local/environment.json
    fi

    # Prepare the database, which will be stored on the host system because
    # the default path (/vagrant/)local/db.sqlite is mapped to this directory's
    # 'local' subdirectory on the host system. Use sudo to run as the vagrant
    # user so that if the database is being created, the vagrant user will
    # have write access instead of it being owned by root.
    python3 manage.py migrate
    python3 manage.py load_modules
    python3 manage.py collectstatic --noinput

    # Give the vagrant user write access to the Sqlite database that was just
    # created by 'migrate', as well as to the directory containing it because
    # Sqlite needs to create a journal file there for write operations.
    chown vagrant.vagrant local/db.sqlite3
    chmod a+w local

    # Configure supervisor to run the uWSGI process and the background notification
    # emails process and start supervisor, which starts the Q uWSGI HTTP server process.
    # Replace '/home/govready-q/.local/bin/' with '' in the supervisor config so it
    # finds uWSGI installed globally, and similarly update the working directory and
    # user.
    yum install -y supervisor
    cp deployment/rhel/supervisor.ini /etc/supervisord.d/govready-q.ini
    sed -i sS/home/govready-q/.local/bin/SS /etc/supervisord.d/govready-q.ini
    sed -i sS/home/govready-q/govready-qS/vagrantS /etc/supervisord.d/govready-q.ini
    sed -i 'sSuser = govready-qSuser = vagrantS' /etc/supervisord.d/govready-q.ini
    service supervisord restart

    # Create a wrapper script to make it easier to run management commands.
    echo 'cd /vagrant && ./manage.py "$@"' > /usr/local/bin/manage
    chmod +x /usr/local/bin/manage
  SHELL
end
