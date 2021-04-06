# Ubuntu 20.04 focal-20210119
FROM ubuntu:focal-20210119

# Update package list.
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

# Set up the locale.
RUN apt-get update && \
  apt-get install -y locales openssh-sftp-server openssh-server xvfb libfontconfig wkhtmltopdf sudo apt-get install libmariadbclient-dev && \
  echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
  dpkg-reconfigure locales && \
  update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en

RUN echo "root:root" | chpasswd && \
  mkdir /var/run/sshd

# SSH setting
COPY deployment/local/ssh /etc/ssh
RUN chmod -R 400 /etc/ssh

# Set up the timezone.
RUN apt-get install -y --no-install-recommends tzdata && \
  ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
  dpkg-reconfigure tzdata

# Install GovReady-Q prerequisites.
RUN apt-get -y install \
  unzip git curl jq \
  python3 python3-pip \
  python3-yaml \
  graphviz pandoc \
  gunicorn

# Put the Python source code here.
WORKDIR /usr/src/app


# Upgrade pip to version 20.1+ - IMPORTANT
RUN python3 -m pip install --upgrade pip
RUN pip3 install ipdb

# This directory must be present for the AppSource created by our
# first_run script. The directory only has something in it if
# the container is launched with --mount.
# --mount type=bind,source="$(pwd)",dst=/mnt/q-files-host
RUN mkdir -p /mnt/q-files-host
