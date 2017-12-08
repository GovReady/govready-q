# Build on Docker's official CentOS 7 image.
FROM centos:7

# Expose the port that `manage.py runserver` uses by default.
EXPOSE 8000

# Put the Python source code here.
WORKDIR /usr/src/app

# Set up the locale - needed for Click, see http://click.pocoo.org/5/python3/
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US:en

# Install Python 3.6 and set up a virtualenv for it.
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install python36u python36u-devel.x86_64 python36u-pip gcc-c++.x86_64 
RUN python3.6 -m venv venv

# Install required system packages.
# jq: we use it to assemble the local/environment.json file
RUN yum install -y graphviz unzip pandoc wkhtmltopdf jq libffi-devel

# Copy in the Python module requirements and install them.
# Manually install database drivers which aren't in our requirements
# file because they're not commonly used in development.
# Run pyup.io's python package vulnerability check.
# Do it all in the Python 3.6 virtualenv.
COPY requirements.txt ./
RUN source venv/bin/activate && \
  pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir psycopg2 && \
  safety check

# Copy in the vendor resources and fetch them.
COPY fetch-vendor-resources.sh ./
RUN ./fetch-vendor-resources.sh

# Copy in remaining source code. (We put this last because these
# change most frequently, so there is less to rebuild if we put
# infrequently changed steps above.)
#
# NOTE: Do *not* include the "local" directory in this step, since
# that often has local development files.
COPY discussion ./discussion
COPY guidedmodules ./guidedmodules
COPY modules ./modules
COPY siteapp ./siteapp
COPY templates ./templates
COPY manage.py .
COPY deployment/docker/manage.sh /usr/local/bin/manage
COPY deployment/docker/dockerfile_exec.sh .

# Set the startup script.
CMD source venv/bin/activate && source ./dockerfile_exec.sh
