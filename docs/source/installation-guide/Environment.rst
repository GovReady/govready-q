Environment Settings
--------------------

Available Configuration Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following environment variables are used to configure your
GovReady-Q instance and can be configured through your local
``local/environment.json`` or passed in as environmental parameters when
launching a container with GovReady-Q.

-  ``admins``: used to configure a display point of contact
   “Administrator” on site and unrelated to the configuration of actual
   administrators configured in the database.
-  ``branding``: used for `custom branding`_.
-  ``db``: if supplied, this is the DB connection used. See `DB
   configuration`_.
-  ``debug``: should be ``false`` or absent in production environments.
   If set to ``true``, turns on certain debug/development settings.
-  ``email``: used to configure access to a mail server for sending and
   receiving email. Object has the following format:
   ``{"host": "smtp.server.com", "port": "587", "user": "...", "pw": "....",   "domain": "webserver.example.com"}``.
   See `Configuring email`_ and `Other Configuration Settings`_. },.
-  ``govready_cms_api_auth``: used to store API key to interact with
   GovReady’s CMS agent and dashboard. Not relevant to most users. See
   `GovReady-CMS-API`_.
-  ``host``: this is the domain name (HTTP ``Host`` header) used for
   root-level GovReady-Q pages. See also ``organization-parent-domain``,
   which is used to construct organization subdomains (if using a
   different base domain).
-  ``https``: set to true to generate HTTPS headers and urls when site
   is running behind a proxy terminating HTTPS connections. See
   `Configuring a Reverse Proxy Webserver for Production Use`_.
-  ``mailgun_api_key``: used to hold API key for using mailgun to
   send/receive emails.
-  ``memcached``: if setting is true, enable a memcached cache using the
   default host/port
-  ``organization-parent-domain``: this is the domain name (HTTP
   ``Host`` header) suffix used for organization-specific GovReady-Q
   pages.
-  ``organization-seen-anonymously``: show list of all created
   organizations to an anonymous (e.g., not signed-in) user on home page
   if set to true.
-  ``secret-key`` - used to make instance more secure by contributing a
   salt value to generating various random strings and hashes. Do not
   share.
-  ``gr-pdf-generator`` - specifies the library/process used to generate PDFs,
   options are `off` and `wkhtmltopdf` and default is `None`.
-  ``gr-img-generator`` - specifies the library/process used to generate images and thumbnails,
   options are `off` and `wkhtmltopdf` and default is `None`.
-  ``single-organization``: used to enforce single organization mode
   with “main” as subdomain of default organization instead of
   multi-tenant with different subdomains for different organizations.
-  ``static``: used to prepend a root path to the default ``/static/``
   URL path for accessing static assets.
-  ``syslog``: used to set the host and port of a syslog-compatible log
   message sink. (Default: None.)
-  ``trust-user-authentication-headers``: used to activate reverse proxy
   authentication. See `Proxy Authentication Server`_.

Production Deployment Environment Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A production system deployment may need to set more options in
``local/environment.json``. Here are recommended settings:

::

   {
     "debug": false,
     "admins": [["Name", "email@domain.com"], ...],
     "host": "q.<yourdomain>.com",
     "https": true,
     "secret-key": "something random here",
     "static": "/root/public_html"
   }

Enterprise Single-Sign On Environment Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GovReady-Q supports Enterprise Login via IAM (Identity and Access
Management). In this configuration, GovReady-Q is deployed behind a
reverse proxy that authenticates users and passes the authenticated
user’s username and email address in HTTP headers.

To activate reverse proxy authentication, add the header names used by
the proxy to your ``local/environment.json``, e.g.:

::

   {
       "trust-user-authentication-headers": {
         "username": "X-Authenticated-User-Username",
         "email": "X-Authenticated-User-Email"
       },
   }

GovReady-Q must be run at a private address that cannot be accessed
except through the proxy server. The proxy server must be configured to
proxy to GovReady-Q’s private address. See `Enterprise Single-Sign On /
Login`_ for additional details.

PDF and Image Generation Environment Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GovReady-Q optionally supports generating PDFs and custom thumbnails for
uploaded files using ``wkhtmltopdf`` and ``wkhtmltoimage``. Admins must
make sure the `wkhtmltopdf` library is installed properly for operating
system being used.

GovReady-Q PDF generation and thumbnails are turned off by default for
security reasons.

PDF generator library ``wkhtmltopdf`` has security issues wherein individuals could add
HTML references such as links or file references inside the documents
they are creating which the PDF Generator blindly interprets. This leads
to SSRF (Server Side Request Forgery) in which data is retrieved from
server and added to PDF by the PDF Generator. An issue also exists
with the sub-dependency of `libxslt` before CentOS 8.x raising CVE vulnerability
with scanners. For these reasons, PDF Generation is being a configurable setting.

To activate PDF and thumbnail generation, add ``gr-pdf-generator`` and
``gr-img-generator`` environmental parameters to your ``local/environment.json``, e.g.:

::

   {
      ...
      "gr-pdf-generator": "wkhtmltopdf",
      "gr-img-generator": "`wkhtmltopdf",
      ...
   }


Custom Branding Environment Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may override the templates and stylesheets that are used for
GovReady-Q’s branding by adding a new key named ``branding`` that is the
name of an installed Django app Python module (i.e. created using
``manage.py startapp``) that holds templates and static files. See
`Applying Custom Organization Branding`_.

.. _Enterprise Single-Sign On / Login: enterprise_sso.html
.. _Applying Custom Organization Branding: CustomBranding.html
