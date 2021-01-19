# Build GovReady-Q Docker container
#
# Build examples:
#   docker build --tag govready/govready-q-0.9.0 .
#
# Run examples:
#   docker run -it -d -p 8000:8000 --name govready-q-0.9.0 --rm govready/govready-q-0.9.0

# Build on Docker's official CentOS 7 image.
FROM centos:centos7.8.2003

# Default to gunicorn instead of uwsgi
ARG SUPERVISORD_INI=deployment/docker/supervisord_gunicorn.ini
ARG DOCKERFILE_EXEC_SH=deployment/docker/dockerfile_exec_gunicorn.sh
# ARG SUPERVISORD_INI=deployment/docker/supervisord_uwsgi.ini
# ARG DOCKERFILE_EXEC_SH=deployment/docker/dockerfile_exec_uwsgi.sh

# Default to "off"
ARG GR_PDF_GENERATOR=off
#ARG GR_PDF_GENERATOR=wkhtmltopdf

# Expose the port that `manage.py runserver` uses by default.
EXPOSE 8000

# Put the Python source code here.
WORKDIR /usr/src/app

# Set up the locale. Lots of things depend on this.
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US:en

# Install required system packages.
# git222: git 2 or later is required for our use of GIT_SSH_COMMAND in AppSourceConnection
# jq: we use it to assemble the local/environment.json file
RUN \
   yum -y install https://repo.ius.io/ius-release-el7.rpm \
&& yum -y update \
&& yum -y install \
    python36u python36u-pip \
    unzip git222 jq nmap-ncat \
    graphviz pandoc \
    supervisor \
    && yum clean all && rm -rf /var/cache/yum

# Upgrade pip to version 20.1+ - IMPORTANT
RUN python3.6 -m pip install --upgrade pip

# install wkhtmltopdf for generating PDFs, thumbnails
# TAKE CAUTION WITH wkhtmltopdf security issues where crafted content renders server-side information
RUN if [ "$GR_PDF_GENERATOR" = "wkhtmltopdf" ] ; then (yum -y install xorg-x11-server-Xvfb wkhtmltopdf && yum clean all && rm -rf /var/cache/yum) ; fi

# Copy in the Python module requirements and install them.
# file because they're not commonly used in development.
COPY requirements.txt ./
RUN pip3.6 install --no-cache-dir -r requirements.txt
# RUN pip3.6 install --no-cache-dir --user -r requirements.txt

# Install database drivers which aren't in our requirements.
RUN \
   yum -y install \
   python36u-devel gcc-c++.x86_64 \
   mysql-devel \
   && yum clean all && rm -rf /var/cache/yum
COPY requirements_mysql.txt ./
RUN pip3.6 install --no-cache-dir -r requirements_mysql.txt

# Remove build libraries needed only for installing packages
RUN \
   yum -y remove \
   python36u-devel.x86_64 python3-devel.x86_64 gcc-c++.x86_64
RUN yum clean all && rm -rf /var/cache/yum

# Remove unneeded Python libraries
# Remove `pipenv` and its extra copies of `requests` and `urllib3` that scanners see
# Safety only needed for preparing requirements files, not operating GovReady
# RUN pip3.6 uninstall -y pipenv safety || true

# Safety only needed for preparing requirements files, not operating GovReady
## Run pyup.io's python package vulnerability check.
#RUN safety check

# Copy in the vendor resources and fetch them.
COPY fetch-vendor-resources.sh ./
RUN ./fetch-vendor-resources.sh
# Confirm that sqlite3 command runs, for users who use it.
RUN sqlite3 --version

# Copy in remaining source code. (We put this last because these
# change most frequently, so there is less to rebuild if we put
# infrequently changed steps above.)
#
# NOTE: Do *not* include the "local" directory in this step, since
# that often has local development files. But *do* include fixtures
# so that tests can be run.
COPY VERSION ./VERSION
COPY controls ./controls
COPY discussion ./discussion
COPY guidedmodules ./guidedmodules
COPY modules ./modules
COPY siteapp ./siteapp
COPY templates ./templates
COPY fixtures ./fixtures
COPY q-files ./q-files
COPY loadtesting ./loadtesting
COPY system_settings ./system_settings
COPY manage.py .
COPY install-govready-q.sh .
COPY quickstart.sh .

# Flatten static files. Create a local/environment.json file that
# has the static directory set and only setting necessary for collectstatic
# to work. It matches what's set in dockerfile_exec.sh.
RUN mkdir -p local && echo '{ "static": "static_root", "debug": false, "host": "_", "https": false }' > local/environment.json
RUN python3.6 manage.py collectstatic --noinput

# Configure supervisord.
# a) Wipe out /var/{run,log} because when these directories are mounted with
#    tmpfs they will be empty, so start them empty so the two setups match.
# b) Make /var/{run,log} world-writable because when we start the container with
#    the non-root user it will need permission to write there.
# c) Move the supervisor log from /var/log/supervisor and the child process logs
#    from /tmp to /var/log to make them all easily accessible if /var/log is mounted
#    to a volume, and similarly the run socket from /var/run/supervisor.
#    Otherwise we have to mess with file permissions so the inner directories are
#    writable, and I couldn't get that to work. Even if the directories had chmod 777
#    the non-root user could not create files inside them.
RUN rm -rf /run/* /var/log/*
RUN chmod a+rwx /run /var/log
RUN sed -i "s:/var/run/supervisor/:/var/run/:" /etc/supervisord.conf
RUN sed -i "s:/var/log/supervisor/:/var/log/:" /etc/supervisord.conf
RUN sed -i "s:^;childlogdir=/tmp:childlogdir=/var/log:" /etc/supervisord.conf
COPY $SUPERVISORD_INI /etc/supervisord.d/application.ini

# Add container startup and management scripts.
COPY $DOCKERFILE_EXEC_SH dockerfile_exec.sh
COPY deployment/docker/first_run.sh /usr/local/bin/first_run
# COPY deployment/docker/uwsgi_stats.sh /usr/local/bin/uwsgi_stats
# COPY deployment/docker/gunicorn_stats.sh /usr/local/bin/gunicorn_stats
COPY deployment/docker/tail_logs.sh /usr/local/bin/tail_logs
COPY deployment/docker/add_data.sh /usr/local/bin/add_data

# This directory must be present for the AppSource created by our
# first_run script. The directory only has something in it if
# the container is launched with --mount.
# --mount type=bind,source="$(pwd)",dst=/mnt/q-files-host
RUN mkdir -p /mnt/q-files-host

# Create a non-root user and group for the application to run as to guard against
# run-time modification of the system and application.
RUN groupadd application && \
    useradd -g application -d /home/application -s /sbin/nologin -c "application process" application && \
    chown -R application:application /home/application
RUN echo -n "the non-root user is: " && grep ^application /etc/passwd

# Give the non-root user access to scratch space.
RUN mkdir -p local
RUN chown -R application:application local

# Move the environment.json to /tmp because in some environments the main
# filesystem is read-only and we won't be able to update local/environment.json
# once the container starts. In those cases, /tmp must be a tmpfs. We use
# /tmp for other purposes at run-time as well. Although we don't need a
# working environment.json file for the remainder of this Dockerfile, downstream
# packagers using 'FROM govready/govready-q' might want to run additional
# management commands, so we'll keep it working.

RUN cp local/environment.json /tmp
RUN chown -R application:application /tmp/environment.json

# Run the container's process zero as this user.
USER application

# Change file permissions to secure file
RUN chmod 0600 /tmp/environment.json

# Create symbolic link
RUN ln -sf /tmp/environment.json local/environment.json

# Test.
RUN python3.6 manage.py check

# Set the startup script.
CMD [ "bash", "dockerfile_exec.sh" ]
