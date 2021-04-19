
See [Installing GovReady-Q Compliance Server on Workstations for Development](https://govready-q.readthedocs.io/en/latest/deploy_local_dev.html) for detailed instructions.

## Local Dev
1. Configure
    - You can configure environment variables for this build by updating `govready-q.env`
        - To prevent upstream changes between pulls - `git update-index --skip-worktree govready-q.env`
        - If you want to allow upstream changes again - `git update-index --no-skip-worktree govready-q.env`
2. Start
    -  `docker-compose up`
3. Debugging
    - `docker attach govready_q`
    - use ipdb as you normally would
4. Connect to Container
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

