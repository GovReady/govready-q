Extra doc text



"govready_admins":[
        {"username": "username", "email":"first.last@example.com", "password": "REPLACEME"}
    ]


+------------+---------------------------------------------------------+
| Container  | Where                                                   |
+============+=========================================================+
| Current    | https://hub.docker.com/r/govready/govready-q/           |
| Release on |                                                         |
| Docker     |                                                         |
+------------+---------------------------------------------------------+
| Release    | `http                                                   |
| 0.9.0.dev  | s://hub.docker.com/r/govready/govready-0.9.0.dev/ <http |
| on Docker  | s://hub.docker.com/r/govready/govready-q-0.9.0.dev/>`__ |
+------------+---------------------------------------------------------+
| Nightly    | https://hub.docker.com/r/govready/govready-q-nightly/   |
| Build on   |                                                         |
| Docker     |                                                         |
+------------+---------------------------------------------------------+

Additional options
------------------

Notes and Common Issues
~~~~~~~~~~~~~~~~~~~~~~~

Your GovReady-Q site will not load immediately, as GovReady-Q
initializes your database for the first time. Wait for the site to
become available.

Because of HTTP Host header checking, you must use ``localhost`` to
access the site, or another hostname if configured using the
``--address`` option documented below.

If the site does not come up, check the container logs for an error
message:

::

   docker container logs govready-q

The GovReady-Q default SQLite database created within a Docker container
exists only for the duration of the container’s lifetime. The database
will persist between
``docker container stop``/``docker container start`` commands, but when
the container is removed from Docker (i.e. using
``docker container rm``) the database will be destroyed. See the
*Persistent database* section below for connecting to a database outside
of the container for production data.

The default Govready-Q instance cannot send email or receive comment
replies until it is configured to use a transactional mail provider like
Mailgun – see below.

The default Govready-Q instance is configured to non-debug mode (Django
``DEBUG=false``), which is the recommended setting for a public website.
The instance can be set to debug mode at runtime – see below.