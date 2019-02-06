Simple IAM Proxy Server
=======================

This project models an identity management reverse proxy server. We use this project to test GovReady-Q's
ability to operate behind an identity management reverse proxy server.

The proxy server handles identity and session management and passes authentication information to
a backend server using HTTP headers:

* When a user visits the proxy server and does not have a session open, they are redirected to
  a log in page served by the proxy server. After login they are redirected back to their original
  request path.
* The IAM server doesn't perform any actual authentication logic. The login page asks for the user's username and email address and passes that information to the backend server as entered.
* When a user with an active login session requests a path, identity information is passed in
  HTTP headers to the backend server along with the proxied request.
* When a user visits the configured logout path, the proxy server deletes the session and then
  redirects the user to the app homepage.

To start the proxy, run:

	python3 iam.py

The proxy's options are controlled by environment variables:

| Variable | Default |
| -------- | ------- |
| BIND_HOST | localhost |
| BIND_PORT | 8000 |
| BACKEND_URL | http://localhost:8001 |
| LOGIN_PATH | /login |
| LOGOUT_PATH | /accounts/logout/ |
| SESSION_COOKIE_NAME | iam_session |
| IAM_USERNAME_HEADER | IAM-Username |
| IAM_EMAIL_HEADER | IAM-Email |

Edit GovReady-Q's `environment.json` file to tell it to trust the two user headers:

```
{
	...
	"trust-user-authentication-headers": {
		"username": "IAM-Username",
		"email": "IAM-Email"
	},
	...
}
```

In a second console, start GovReady-Q:

	cd ../..
	./manage.py runserver localhost:8001

In the default configuration, the proxy server is listening at http://localhost:8000 and forwards to the backend GovReady-Q server listening on port 8001. GovReady-Q is configured in `local/environment.json` to know what its public URL is, and the default `http://localhost:8000` will correctly match this setup.

You can also try starting up GovReady-Q using our docker image:

	deployment/docker/docker_container_run.sh --relaunch --bind 8001 -- -e PROXY_AUTHENTICATION_USER_HEADER=IAM-Username -e PROXY_AUTHENTICATION_EMAIL_HEADER=IAM-Email

---
