# README

See [Installing GovReady-Q Compliance Server on Workstations for Development](https://govready-q.readthedocs.io/en/latest/deploy_local_dev.html) for detailed instructions.

## Local Dev
1. Start
    -  `docker-compose up`
2. Debugging
    - `docker attach govready_q`
    - use ipdb as you normally would
3. Connect to Container
    - `docker exec -it govready_q /bin/bash`