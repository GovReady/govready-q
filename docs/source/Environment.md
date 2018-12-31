Environment Settings
====================

A production system may need to set more options in `local/environment.json`. Here are recommended settings:

	{
	  "debug": false,
	  "admins": [["Name", "email@domain.com"], ...],
	  "host": "q.<yourdomain>.com",
	  "https": true,
	  "organization-parent-domain": "<yourdomain>.com",
	  "organization-seen-anonymously": false,
	  "secret-key": "something random here",
	  "static": "/root/public_html"
	}

Custom Branding
---------------

You may override the templates and stylesheets that are used for GovReady-Q's branding by adding a new key named `branding` that is the name of an installed Django app Python module (i.e. created using `manage.py startapp`) that holds templates and static files.

Enterprise Login
----------------

### Proxy Authentication Sever

GovReady-Q can be deployed behind a reverse proxy that authenticates users and passes the authenticated user's username and email address in HTTP headers. In this configuration:

* The user points their browser to the reverse proxy authentication server.
* The proxy authenticates users and proxies the request to GovReady-Q if and only if the user is authenticated and authorized to access GovReady-Q. The proxy passes the user's username and email address in HTTP headers of the proxy's choosing. 
* GovReady-Q will create a user account for a new user or treat the user as logged in as soon as the user requests a page. Therefore, there is no sign-up or log-in process within GovReady-Q when a proxy authentication server is used.
* All other authentication methods to GovReady-Q are disabled when proxy authentication is enabled. Therefore you should ensure that the Django admin's username matches the admin's username as provided by the proxy server. Otherwise, you will lose access to the admin page. However, if there is a mismatch, you may disable proxy authentication, log in to the Django admin with your admin username and password, and change your admin username to match the username sent by the proxy server.
* GovReady-Q must be run at a private address that cannot be accessed except through the proxy server.

To activate reverse proxy authentication, add the header names used by the proxy to your `local/environment.json`, e.g.:

	{
	  "trust-user-authentication-headers": {
	    "username": "X-Authenticated-User-Username",
	    "email": "X-Authenticated-User-Email"
	  },
	}

The proxy server must be configured to proxy to GovReady-Q's private address. But the `host` and `https` settings in GovReady-Q's `local/environment.json` file must reflect the host and protocol used in the URL the *end user* uses to access GovReady-Q. They do *not* need to match the address that the proxy server uses to reach the GovReady-Q server.

Per the [Django Documentation](https://docs.djangoproject.com/en/dev/howto/auth-remote-user/) on authentication using REMOTE_USER, you must be sure that your proxy server always sets or strips the special username and email headers, including headers that normalize to the same Django key (in particular headers with underscores), from the client request and **does not permit an end-user to submit a fake (or “spoofed”) header value**.

We have an example reverse proxy authentication server at https://github.com/GovReady/govready-q/tree/master/tools/simple_iam_proxy_server which can be used for debugging purposes.
