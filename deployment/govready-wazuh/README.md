# GovReady-Q and Wazuh via Docker Compose

## Overview

This directory contains configuration files that run TKTK

Use [Docker Compose](https://docs.docker.com/compose/) to manage the multi-container app.

Docker Compose commands are similar to, but different from, regular Docker commands.  Read the Docker Compose docs for more details.

## Set Up A Docker Host

### Workstation

[Install Docker](https://docs.docker.com/install/) and Docker Compose on your workstation.

* On Mac and Windows, Docker Compose is included as part of the Docker install.
* On Linux, after installing Docker, [install Docker Compose](https://docs.docker.com/compose/install/#install-compose). Also, you may want to [grant non-root users access to run Docker containers](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

### Docker Machine

[Docker Machine](https://docs.docker.com/machine/) can be used to set up Docker host on either a local or cloud server.  Once you have configured your shell to connect to a Docker host set up by Docker Machine, the Docker Compose commands you need to use will be the same as if you were using the Docker engine running on your workstation as the Docker host.

## Get This Kit

Get the files by cloning the GovReady-Q repository.

```
git clone https://github.com/GovReady/govready-q.git
cd govready-q/deployment/govready-wazuh/
```

**Make sure you are in the `docker-compose-nginx` directory.**

Any `docker-compose` commands will need the `docker-compose.yml` file to know which containers to operate on.

## Run GovReady-Q + Wazuh Multi-container App

To start the containers:

```bash
docker-compose up -d
```

Using the `-d` detaches the containers and runs them in the background.

If you prefer, you can omit `-d`, and then output will be printed to your console window.  If you hit `^C`, the containers will shut down gracefully.  If you hit `^C^C` they will be terminated immediately.

TKTK Two containers will be created, one for each "service" (as they're called in Docker Compose).

TKTK Docker Compose gives these containers names like `docker-compose-nginx_govready-q_1` and `docker-compose-nginx_nginx_1`.  These are three-part names, with the parts separated by underscores.  `docker-compose-nginx` comes from the name of this project (the directory it's in). The second element is the service name (`govready-q` or `nginx`). The third element is a serial number (ascending from 1) for multiple instances of the same service.  The `docker-compose.yml` file here only specifies one instance, so the number will always be `1`.

You can check the status of the containers:

```bash
docker-compose ps
```

## Specify Parameters

Before starting the containers, you can specify which GovReady-Q image to use, which database host to use, and the hostname of the Docker host.  It's important to specify the correct hostname if you are using real TLS certs.

Set these environment variables (sample values provided, replace with your own values):

```bash
export GOVREADY_Q_HOST=ec2-nnn-nnn-nnn-nnn.us-east-1.compute.amazonaws.com
export GOVREADY_Q_DBURL=postgres://govready_q:my_private_password@grq-002.cog63arfw9bib.us-east-1.rds.amazonaws.com/govready_q
export GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0

```

After setting the variables, continue with the "Run GovReady-Q + Wazuh Multi-container App" section above.

If you don't set enviroment variables, these defaults are used:

```bash
export GOVREADY_Q_HOST=test.example.com
export GOVREADY_Q_DBURL=
export GOVREADY_Q_IMAGENAME=govready/govready-q

```

When no DBURL is specified, GovReady-Q uses an internal sqlite database.

## Check Logs From A Container

Check the logs by specifying the service name:

```bash
docker-compose logs govready-q
```

```bash
docker-compose logs nginx
```

## GovReady-Q Is Up

GovReady-Q will boot up, and be ready to answer web requests in 20-30 seconds.

It will answer HTTP on the standard port, 80, and HTTPS on the standard port, 443.

Visit https://localhost/.  (Or `http://localhost`, which will be redirected to https by `nginx`.)

The default hostname used for this project is `test.example.com`.  To check it, put this entry in your `/etc/hosts` file:

```
127.0.0.1       test.example.com
```

When you have `/etc/hosts` set up, visit https://test.example.com/

## Execute A Script In A Container

You can exec a script inside one of the containers by specifying the service name.  Unlike normal `docker`, you do *not* specify `-it` to make the exec interactive.

Here we are executing the `first_run` script inside the `govready-q` service/container.

```bash
docker-compose exec govready-q first_run
```

## Stop And Remove Containers

To stop and remove containers:

```bash
docker-compose down
```
