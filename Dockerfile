# Build on Docker's official CentOS 7 image.
FROM centos:7

# Expose the port that `manage.py runserver` uses by default.
EXPOSE 8000

# Put the Python source code here.
WORKDIR /usr/src/app

# Set up the locale. Lots of things depend on this.
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US:en

# Install required system packages.
# git2u: git 2 or later is required for our use of GIT_SSH_COMMAND in AppSourceConnection
# jq: we use it to assemble the local/environment.json file
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install \
	python36u python36u-devel.x86_64 python36u-pip gcc-c++.x86_64 \
	unzip git2u jq nmap-ncat \
	graphviz pandoc xorg-x11-server-Xvfb wkhtmltopdf \
	supervisor \
	mysql-devel \
	&& yum clean all && rm -rf /var/cache/yum

# Copy in the Python module requirements and install them.
# Manually install database drivers which aren't in our requirements
# file because they're not commonly used in development.
COPY requirements.txt ./
RUN pip3.6 install --no-cache-dir -r requirements.txt

# Run pyup.io's python package vulnerability check.
RUN safety check

# Copy in the vendor resources and fetch them.
COPY fetch-vendor-resources.sh ./
RUN ./fetch-vendor-resources.sh

# Copy in remaining source code. (We put this last because these
# change most frequently, so there is less to rebuild if we put
# infrequently changed steps above.)
#
# NOTE: Do *not* include the "local" directory in this step, since
# that often has local development files. But *do* include fixtures
# so that tests can be run.
COPY VERSION ./VERSION
COPY discussion ./discussion
COPY guidedmodules ./guidedmodules
COPY modules ./modules
COPY siteapp ./siteapp
COPY templates ./templates
COPY fixtures ./fixtures
COPY manage.py .

# Flatten static files. Create a local/environment.json file that
# has the static directory set and only setting necessary for collectstatic
# to work. It matches what's set in dockerfile_exec.sh.
RUN mkdir -p local && echo '{ "static": "static_root", "debug": false, "host": "_", "https": false }' > local/environment.json
RUN python3.6 manage.py collectstatic --noinput

# Configure supervisord.
# a) Make /var/{run,log}/supervisor world-writable because we start supervisord
# as the non-root application user and the OS package makes these paths
# writable only by root. When the container is run with a read-only root
# filesystem, /var/{run,log} must be mounted with --tmpfs (or a writable volume)
# and in this case the directories will be empty on container start, so
# the OS package directory layout won't be there, and we must make the directorries
# world-writable so that the container can create the inner 'supervisor'
# directory (see dockerfile_exec.sh).
# b) Move the child process logs from /tmp to /var/log/supervisor to make them
# more easily accessible if /var/log is mounted to a volume.
RUN chmod a+rwx /run /run/supervisor /var/log /var/log/supervisor
RUN sed -i "s:^;childlogdir=/tmp:childlogdir=/var/log/supervisor:" /etc/supervisord.conf
COPY deployment/docker/supervisord.ini /etc/supervisord.d/application.ini

# Add container startup and management scripts.
COPY deployment/docker/dockerfile_exec.sh .
COPY deployment/docker/first_run.sh /usr/local/bin/first_run
COPY deployment/docker/uwsgi_stats.sh /usr/local/bin/uwsgi_stats
COPY deployment/docker/tail_logs.sh /usr/local/bin/tail_logs

# This directory must be present for the AppSource created by our
# first_run script. The directory only has something in it if
# the container is launched with --mount.
RUN mkdir -p /mnt/apps

# Create a non-root user and group for the application to run as to guard against
# run-time modification of the system and application.
RUN groupadd application && \
    useradd -g application -d /home/application -s /sbin/nologin -c "application process" application && \
    chown -R application:application /home/application

# Give the non-root user access to scratch space.
RUN mkdir -p local
RUN chown -R application:application local

# Move the environment.json to /tmp because in some environments the main
# filesystem is read-only and we won't be able to update local/environment.json
# once the container starts. In those cases, /tmp must be a tmpfs. We use
# /tmp for other purposes at run-time as well.
RUN ln -sf /tmp/environment.json local/environment.json

# Run the container's process zero as this user.
USER application

# Set the startup script.
CMD [ "bash", "dockerfile_exec.sh" ]
