# README

See [Deploying GovReady-Q with Docker](https://govready-q.readthedocs.io/en/latest/deploy_docker.html) for detailed instructions.

#### Build with Gunicorn or uWSGI

The default HTTP server used with GovReady-Q is the [Green Unicorn (Gunicorn)](https://gunicorn.org/).  Optionally, you can build a Docker image that uses [uWSGI server](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html) instead of Gunicorn.  This feature is in preview, and isn't included in the regular documentation yet.

Only the `docker build` commands are different.  Running either flavor of container works the same.

##### Build with Gunicorn

Use either

```
docker image build --tag my-govready-q .  # uses defaults
```

or

```
docker image build --tag my-govready-q --build-arg SUPERVISORD_INI=deployment/docker/supervisord_gunicorn.ini --build-arg DOCKERFILE_EXEC_SH=deployment/docker/dockerfile_exec_gunicorn.sh .
```

##### Build with uWSGI

```
docker image build --tag my-govready-q --build-arg SUPERVISORD_INI=deployment/docker/supervisord_uwsgi.ini --build-arg DOCKERFILE_EXEC_SH=deployment/docker/dockerfile_exec_uwsgi.sh .
```


#### GovReady-Q on Docker Hub

| Container                 | Where                                                                                                           |
|---------------------------|-----------------------------------------------------------------------------------------------------------------|
| Current Release on Docker | [https://hub.docker.com/r/govready/govready-q/](https://hub.docker.com/r/govready/govready-q/)                  |
| Release 0.9.0.dev on Docker | [https://hub.docker.com/r/govready/govready-0.9.0.dev/](https://hub.docker.com/r/govready/govready-q-0.9.0.dev/)                  |
| Nightly Build on Docker   | [https://hub.docker.com/r/govready/govready-q-nightly/](https://hub.docker.com/r/govready/govready-q-nightly/)  |

