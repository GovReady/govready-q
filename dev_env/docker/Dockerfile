# Ubuntu 20.04 focal-20210119
FROM ubuntu:focal-20210119

# Update package list.
ENV DEBIAN_FRONTEND=noninteractive

# Set up the locale.
RUN apt-get update && \
  apt-get install -y locales openssh-sftp-server openssh-server xvfb libfontconfig libmariadbclient-dev && \
  echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
  dpkg-reconfigure locales && \
  update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en

RUN echo "root:root" | chpasswd && \
  mkdir /var/run/sshd

# Set up the timezone.
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
  ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
  dpkg-reconfigure tzdata

# Install GovReady-Q prerequisites.
RUN apt-get update && apt-get -y install \
  unzip git curl jq \
  python3 python3-pip \
  python3-yaml \
  graphviz pandoc \
  gunicorn

ENV CHROME_VERSION "google-chrome-stable"
RUN sed -i -- 's&deb http://deb.debian.org/debian jessie-updates main&#deb http://deb.debian.org/debian jessie-updates main&g' /etc/apt/sources.list \
  && apt-get update && apt-get install wget -y
ENV CHROME_VERSION "google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list \
  && apt-get update && apt-get -qqy install ${CHROME_VERSION:-google-chrome-stable}

# Chromium for Headless Selenium tests
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV DISPLAY=:99

# Put the Python source code here.
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y wkhtmltopdf;

# Upgrade pip to version 20.1+ - IMPORTANT
RUN python3 -m pip install --upgrade pip
RUN pip3 install ipdb

# This directory must be present for the AppSource created by our
# first_run script. The directory only has something in it if
# the container is launched with --mount.
# --mount type=bind,source="$(pwd)",dst=/mnt/q-files-host
RUN mkdir -p /mnt/q-files-host
