
See [Installing GovReady-Q Compliance Server on Workstations for Development](https://govready-q.readthedocs.io/en/latest/deploy_local_dev.html) for detailed instructions.

## Local Dev
1. Start
    -  `docker-compose up`
2. Debugging
    - `docker attach govready_q`
    - use ipdb as you normally would
3. Connect to Container
    - `docker exec -it govready_q /bin/bash`
    
    
## IDE Interpreter Steps

### Pycharm
#### Automated Sync via SSH Interpreter
- `File -> Settings -> Project -> Project Interpreter  -> Cog -> Add -> SSH Interpreter`
    - Host: `localhost`
    - Port: `2222`
    - User: `root`
    - Password: `root`
    - Interpreter: `/usr/src/app/deployment/local/remote_interpreter/python_env.sh`

### VIM
- `docker exec -it govready_q /bin/bash` - Connect to the Django container directly to code.
- Code is synced in realtime.  Your code changes will be reflected on the host and will not be lost.

