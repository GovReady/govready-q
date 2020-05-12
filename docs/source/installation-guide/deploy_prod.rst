Deploying GovReady-Q in Production environments
===============================================

These instructions assume that GovReady-Q is installed by the user
``govready-q``, in the directory ``/home/govready-q/govready-q/``.

To verify that this is the case, run the following command, and check
whether GovReady-Q responds to HTTP requests (on ``localhost:8000`` by
default).

::

   cd /home/govready-q/govready-q/ && python3 manage.py runserver

If GovReady-Q is installed successfully, proceed with the rest of these
configuration instructions. If it doesn’t, see `OS-specific install
instructions <deploy_all.html>`__.

Set basic configuration variables
---------------------------------

Create a file named ``local/environment.json`` (ensure it is not
world-readable) that contains site configuration in JSON, with some
recommended settings:

::

   {
     "debug": false,
     "host": "webserver.hostname.com",
     "https": true,
     "secret-key": "generate random string using e.g. https://www.miniwebtool.com/django-secret-key-generator/",
     "static": "/home/govready-q/public_html/static"
   }

Because of host header checking, to test the site again using
``python3 manage.py runserver`` you will need to visit it using
``webserver.hostname.com`` and not ``localhost``. (Be sure to replace
``webserver.hostname.com`` with your hostname.)

Remember to Define Your ``host``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **DisallowedHost…Invalid HTTP_HOST header…You may need to add ‘’ to
ALLOWED_HOSTS** is a common error received when first trying to get
GovReady-Q running on a server at a specific domain. The error indicates
the domain you are trying to visit is not white listed in Django’s
special ``ALLOWED_HOST`` variable.

For security, Django requires white listing your server’s domain(s) in
the ``ALLOWED_HOST`` variable. Ordinarily this is hardcoded into the
``settings.py`` file. GovReady-Q allows the ``ALLOWED_HOST`` to be set
by the ``host`` environment settings so the values can be passed at
runtime.

-  ``host`` must be defined, or GovReady-Q will default value to
   ``localhost``

Setting up the Database Server
------------------------------

For production deployment, it is recommended to use dedicated database
software, rather than SQLite.

The recommended database is PostgreSQL - see `instructions on setting up
Q with PostgreSQL <configure_db.html>`__

Setting up a Webserver
----------------------

It’s recommended to run a dedicated webserver software, such as Apache
or Nginx, as a reverse proxy in front of the Q application (running
through uWSGI). To read how to do this, see `instructions on setting up
Q with a reverse proxy webserver <configure_webserver.html>`__.

Creating the First User
-----------------------

Create the initial user and a “main” organization using:

::

   python3 manage.py first_run

You should now be able to log into GovReady-Q using the user created in
this section.

You can also use the Django admin to create organizations.

Other Configuration Settings
----------------------------

Set up email by adding to ``local/environment.json``:

::

     "admins": [["Your Name", "you@company.com"]],
     "email": {
       "host": "smtp.server.com", "port": "587", "user": "...", "pw": "....",
       "domain": "webserver.hostname.com"
     },
     "mailgun_api_key": "...",

Updating Deployment
-------------------

When there are changes to the GovReady-Q software, pull new sources and
restart processes with:

::

   # replace $DISTRO with an appropriate value.
   # Currently-supported options include "rhel" and "ubuntu"
   sudo -iu govready-q /home/govready-q/govready-q/deployment/$DISTRO/update.sh

As root, you can also restart just the Python/Django process:

::

   sudo supervisorctl restart all

But this won’t do a full update so don’t normally do that (it won’t
restart the separate notifications process or generate static assets,
etc.).
