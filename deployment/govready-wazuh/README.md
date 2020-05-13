gected to https.)

You will need to bypass browser warnings about the untrusted self-signed certificate.

## Execute A Script In A Container

You can exec a script inside one of the containers by specifying the service name.  Unlike normal `docker`, you do *not* specify `-it` to make the exec interactive.

Here we are executing the `first_run` script inside the `govready-q` service/container.

```bash
docker-compose exec govready-q first_run
```

## Stop And Remove Containers

To stop and remove containers:

```bash
docker-compose down
```

## Cleaning up

### To remove the Docker images installed in this document

To remove the Govready and Wazuh images downloaded by following the instructions above:

```bash
docker-compose down --rmi all
```

### To delete all Docker containers and images

**Caution!**

The following notes describe how to delete every Docker container and every Docker image on your machine.

```
# Must be run first because images are attached to containers
docker rm -f $(docker ps -a -q)

# Delete every Docker image
docker rmi -f $(docker images -q)
```
