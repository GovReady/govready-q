# GovReady-Q and nginx via Docker Compose

A list of [deployment guides](https://govready-q.readthedocs.io/en/latest/introduction.html#installing-govready-q) for installing and deploying GovReady-Q can be found in the official [GovReady-Q documentation](https://govready-q.readthedocs.io).

This directory contains configuration files that run two Docker containers, one for GovReady-Q and the other for nginx.  nginx is used in a reverse proxy configuration, to handle incoming HTTP requests, which it then passes to GovReady-Q.

This configuration is under development; in the future, nginx will be used to terminate HTTPS for GovReady-Q.  Additional documentation will be available when it is finished.