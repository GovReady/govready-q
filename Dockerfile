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
	unzip git2u jq \
	graphviz pandoc xorg-x11-server-Xvfb wkhtmltopdf \
	mysql-devel \
	&& yum clean all && rm -rf /var/cache/yum

# Copy in the Python module requirements and install them.
# Manually install database drivers which aren't in our requirements
# file because they're not commonly used in development.
COPY requirements.txt ./
RUN pip3.6 install --no-cache-dir -r requirements.txt
RUN pip3.6 install --no-cache-dir mysqlclient==1.3.12 # GPL

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

# Add container startup scripts.
COPY deployment/docker/dockerfile_exec.sh .
COPY deployment/docker/first_run.sh .

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
