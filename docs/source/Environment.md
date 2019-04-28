## Environment Settings

### top-level keys

- `admins`
- `branding`: used for [custom branding](Custombranding.html)
- `db`: if supplied, this is the DB connection used. See [DB configuration](configure_db.html).
- `debug`: should be `false` or absent in production environments. If set to `true`, turns on certain debug/development settings.
- `email` <!-- this seems to be a multi-level key -->
- `govready_cms_api_auth`
- `host`: this is the domain name (HTTP `Host` header) used for root-level GovReady-Q pages. See also `organization-parent-domain`, which is used to construct organization subdomains (and which has a different default value!).
- `https`
- `mailgun_api_key`
- `memcached`
- `organization-parent-domain`: this is the domain name (HTTP `Host` header) suffix used for organization-specific GovReady-Q pages. The default value is `localhost:80`, regardless of the value supplied for `host` - if you have set the `host` key, and intend to use organization subdomains, you will almost certainly want to set `organization-parent-domain` as well.
- `organization-seen-anonymously`
- `secret-key`
- `single-organization`
- `static`
- `syslog`
- `trust-user-authentication-headers`

### Production Deployment Environment Settings

A production system deployment may need to set more options in `local/environment.json`. Here are recommended settings:

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

### Enterprise Single-Sign On Environment Settings

GovReady-Q supports Enterprise Login via IAM (Identity and Access Management). In this configuration, GovReady-Q is deployed behind a reverse proxy that authenticates users and passes the authenticated user’s username and email address in HTTP headers.

To activate reverse proxy authentication, add the header names used by the proxy to your `local/environment.json`, e.g.:

  {
    "trust-user-authentication-headers": {
      "username": "X-Authenticated-User-Username",
      "email": "X-Authenticated-User-Email"
    },
  }


GovReady-Q must be run at a private address that cannot be accessed except through the proxy server. The proxy server must be configured to proxy to GovReady-Q's private address. See [Enterprise Single-Sign On / Login](enterprise_sso.html) for additional details.

### Custom Branding Environment Settings

You may override the templates and stylesheets that are used for GovReady-Q's branding by adding a new key named `branding` that is the name of an installed Django app Python module (i.e. created using `manage.py startapp`) that holds templates and static files. See [Applying Custom Organization Branding](CustomBranding.html).
