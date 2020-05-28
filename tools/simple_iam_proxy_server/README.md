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

Use the authentication headers appropriate for your environment.  For instance, to use `ICAM_DISPLAYNAME` and `ICAM_EMAIL_ADDRESS`, use this command instead:

	deployment/docker/docker_container_run.sh --relaunch --bind 8001 -- -e PROXY_AUTHENTICATION_USER_HEADER=ICAM_DISPLAYNAME -e PROXY_AUTHENTICATION_EMAIL_HEADER=ICAM_EMAIL_ADDRESS

Running Simple IAM Proxy Server with Docker
---------------------------------------------------------

This directory includes a Dockerfile which will build a Docker image for running the Simple IAM Proxy Server.

To build the default image:

	docker image build --tag govready/simple-iam-proxy .

To build an "ICAM" image that overrides the default names of the authentication headers (to match the second `docker_container_run.sh` example above):

	docker image build --tag govready/simple-iam-proxy-icam -f Dockerfile-ICAM .

To start the proxy, run:

	docker container run -it --rm -p 8000:8000 govready/simple-iam-proxy

Or for the ICAM version, run:

	docker container run -it --rm -p 8000:8000 govready/simple-iam-proxy-icam

Since `-it` is specified, the debug output will be printed to the console.  When you're ready, use `^C` to stop the container.  Since `--rm` is specified, the container will be automatically removed when you stop it.

Environment variables can be used as above.  Because of Docker networking, `BIND_HOST` is defaulted to `0.0.0.0`, and `BACKEND_URL` is defaulted to `http://host.docker.internal:8001`. (`host.docker.internal` is the address for your Docker host; it is equivalent to `localhost` from the directions above.)

You can override `BIND_HOST` and `BACKEND_URL`, but be mindful of the Docker networking concerns, or you may not be able to connect to the proxy server, or the proxy server may not be able to connect to your local computer.

---
