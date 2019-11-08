# Build on Docker's official CentOS 7 image.
#FROM centos:7
FROM docker.cbp.dhs.gov/cloud/python:3.6

# Expose the port that `manage.py runserver` uses by default.
# Ports are exposed by marathon, so  not necessary to specify.
# EXPOSE 8000

# Put the Python source code here.
WORKDIR /usr/src/app

# Set up the locale. Lots of things depend on this.
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US:en

# Install required system packages.
# git2u: git 2 or later is required for our use of GIT_SSH_COMMAND in AppSourceConnection
# jq: we use it to assemble the local/environment.json file
# FIX FOR CBP: Try to put ius git2u and related files into Artifactory
# RUN \
#   yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
# Run yum -y update
RUN yum -y install \
	python36u python36u-devel.x86_64 python36u-pip gcc-c++.x86_64 \
	unzip git2u jq nmap-ncat \
	graphviz pandoc xorg-x11-server-Xvfb wkhtmltopdf \
	supervisor \
	mysql-devel \
	&& yum clean all && rm -rf /var/cache/yum

# Create a non-root user and group for the application to run as to guard against
# run-time modification of the system and application.
RUN groupadd -g 501 application && \
    useradd -u 501 -g application -d /home/application -s /sbin/nologin -c "application process" application && \
    chown -R application:application /home/application
RUN echo -n "the non-root user is: " && grep ^application /etc/passwd

# Give the non-root user access to scratch space.
RUN mkdir -p local
RUN chown -R application:application local

# Copy in the Python module requirements and install them.
# Manually install database drivers which aren't in our requirements
# file because they're not commonly used in development.
COPY src/requirements.txt ./
COPY src/requirements_mysql.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r requirements_mysql.txt

# Run pyup.io's python package vulnerability check.
# FIX FOR CBP: We probably cannot run the safety check because we will not see public Internet
#RUN safety check

# Copy in the vendor resources and fetch them.
#COPY src/fetch-vendor-resources.sh ./
# FIX FOR CBP: Figure out how to put 3rd party vendor assets into artifactory and retrieve from artifactory
# because CBP will not let us retrieve from the public internet
#RUN ./fetch-vendor-resources.sh

# Copy in remaining source code. (We put this last because these
# change most frequently, so there is less to rebuild if we put
# infrequently changed steps above.)
#
# NOTE: Do *not* include the "local" directory in this step, since
# that often has local development files. But *do* include fixtures
# so that tests can be run.
COPY src/VERSION ./VERSION
RUN chown 501:501 ./VERSION
RUN chmod 555 ./VERSION
COPY src/discussion ./discussion
COPY src/guidedmodules ./guidedmodules
COPY src/modules ./modules
COPY src/siteapp ./siteapp
COPY src/templates ./templates
COPY src/fixtures ./fixtures
COPY src/q-files ./q-files
COPY src/testmocking ./testmocking
COPY src/system_settings ./system_settings
COPY src/manage.py .
COPY src/static_root ./static_root
RUN chown -R 501:501 ./discussion ./guidedmodules ./modules ./siteapp ./templates ./fixtures ./q-files ./system_settings ./testmocking ./manage.py ./static_root
RUN chmod -R 755 ./discussion ./guidedmodules ./modules ./siteapp ./templates ./fixtures ./q-files ./system_settings ./testmocking ./manage.py ./static_root

# Flatten static files. Create a local/environment.json file that
# has the static directory set and only setting necessary for collectstatic
# to work. It matches what's set in dockerfile_exec.sh.
RUN mkdir -p local && echo '{ "static": "static_root", "debug": false, "host": "_", "https": false }' > local/environment.json
# FIX FOR CBP: Uncomment this line after we are correctly fetching 3rd party vendor assets
#RUN python manage.py collectstatic --noinput

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
COPY src/deployment/docker/supervisord.ini /etc/supervisord.d/application.ini
RUN chown 501:501 /etc/supervisord.d/application.ini

# Add container startup and management scripts.
COPY src/deployment/docker/dockerfile_exec.sh .
RUN chown 501:501 dockerfile_exec.sh
RUN chmod 755 dockerfile_exec.sh
COPY src/deployment/docker/first_run.sh /usr/local/bin/first_run
COPY src/deployment/docker/uwsgi_stats.sh /usr/local/bin/uwsgi_stats
COPY src/deployment/docker/tail_logs.sh /usr/local/bin/tail_logs
RUN chown -R 501:501 /usr/local/bin/first_run /usr/local/bin/uwsgi_stats /usr/local/bin/tail_logs*

# This directory must be present for the AppSource created by our
# first_run script. The directory only has something in it if
# the container is launched with --mount.
RUN mkdir -p /mnt/apps
RUN chown -R 501:501 /mnt/apps

# Move the environment.json to /tmp because in some environments the main
# filesystem is read-only and we won't be able to update local/environment.json
# once the container starts. In those cases, /tmp must be a tmpfs. We use
# /tmp for other purposes at run-time as well. Although we don't need a
# working environment.json file for the remainder of this Dockerfile, downstream
# packagers using 'FROM govready/govready-q' might want to run additional
# management commands, so we'll keep it working.
RUN cp local/environment.json /tmp
RUN chown -R application:application /tmp/environment.json
RUN ln -sf /tmp/environment.json local/environment.json
RUN chown -R application:application local

# Run the container's process zero as this user.
USER application

# Test.
#RUN python manage.py check

# Set the startup script.
# FIX FOR CBP: Commands in `dockerfile_exec.sh` will need to be changed for CBP's Docker images.
CMD [ "bash", "./dockerfile_exec.sh" ]