.. Copyright (C) 2020 GovReady PBC

.. _advanced_container_configuration_example:

Advanced Container Configuration Example
========================================

Below is a diagram of an advanced configuration of GovReady-Q regularly used in an enterprise deployment.

.. figure:: assets/diagram-arch-enterprise-sso-https.png
   :scale: 100 %
   :alt: Deployment architecture behind enterprise Single Sign On proxy

.. 
   vizgraph for the diagram
    graph G {
    rankdir=LR;
    node [shape=rectangle border=black fontsize=11];
    edge [fontsize=10];
        subgraph cluster_0 {
            style=filled;
            color=lightgrey;
            node [style=filled,color=white];
            "gunicorn\nWSGI" -- "GovReady-Q\ngovready-prod.ourco.com";
            label = "GovReady Container";
        }
           "User\nbrowser" -- "Enterprise\nSSO proxy\ngovready.ourco.com" [label="HTTPS A"];
           "Enterprise\nSSO proxy\ngovready.ourco.com" -- "gunicorn\nWSGI" [label="HTTPS B"];
           "GovReady-Q\ngovready-prod.ourco.com" -- "PostgreSQL\n(MySQL)" [label="HTTPS C"];
           "GovReady-Q\ngovready-prod.ourco.com" -- "Enterprise\nemail"
    }

From left to right, this diagram shows the User browser connecting to a enterprise Single Sign On Proxy
which connects to the GovReady-Q container.
The GovReady container is running the GovReady-Q server behind a "gunicorn" (Green Unicorn) web server/WSGI that
serves static assets and terminates the HTTPS connection.
The GovReady-Q server is connected to a persistent PostgreSQL (MySQL) database that is running
on a separate host as well as an enterprise email service.

There are three distinct HTTPS connections in this architecture labeled "HTTPS A", "HTTPS B", and "HTTPS C" requiring
three distinct domains and corresponding certificates. The first connection is between the user browser and the SSO proxy.
The domain that uses perceive as the address of GovReady-Q (e.g., govready.ourco.com) points to the SSO proxy. The second
HTTPS connection is a behind-the-scenes connection between the SSO proxy and GovReady-Q which is assigned a different domain
users never see (e.g., govready-prod.ourco.com). The final HTTPS connection encrypts the communications
between GovReady-Q and its persistent database. (Depending on your deployment configuration, it may not be
necessary to have connections "B" and "C" be encrypted via HTTPS.)

The operate correctly in this configuration, the following options would need to be set.

-  ``HOST = govready.ourco.com`` - to tell GovReady-Q to re-write URLS correctly for the user's browser
-  ``HTTPS = true`` - to tell GovReady-Q to re-write URLs to start with ``https://`` instead of ``http://``
-  ``ALLOWED_HOSTS = ["govready-prod.ourco.com"]`` - to tell GovReady-Q to accept requests being made to domain GovReady-Q is operating at
-  ``DBURL ="db": "postgresql://govready_q:THEPASSWORDHERE@dbserver.hostname.com/govready_q?sslmode=verify-full&sslrootcert=/home/govready-q/pgsql.crt",`` - to tell GovReady-Q how to connect to the database securely
-  ``email-host = smtp.company.org`` - to 
-  ``email-port = 587`` - to 
-  ``email-user = username`` - to 
-  ``email-pw = email_password`` - to 
-   ``email-domain = q.company.org`` - to 
-  ``DEBUG = false`` - because this is a production deployment and we do not want to show debug parameters.

Also, the TLS certificates will need to be copied into the GovReady container (or made available via a mounted volume)
and  ``gunicorn.conf.py`` would need the following values (adjusted correctly for the path to the certificates):

::

   import multiprocessing
   bind = '0.0.0.0:8000'
   workers = 1
   worker_class = 'gevent'
   keepalive = 10
   ca_certs = '/etc/pki/root+intermediate.cer'
   keyfile = '/etc/pki/govready.key'
   certfile = '/etc/pki/govready.cer'
   ssl_version = 'TLSv1_2'

.. topic:: Next

    .. toctree::
        :maxdepth: 1

        advanced-container-config