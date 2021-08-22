# Local Dev
## Required Dependencies
You need to install the following do deploy a development stack:

    - python (3+)
    - docker
    - docker-compose
    
This also assumes you can run as root/administrator.  This is due to ports being opened & docker access.

Allocate to Docker as much Memory, Swap, and CPUS as you can. For example, GovReady-Q performs much better on a 2015 Quad-Core MacBook Pro with CPUs: 3, Memory: 9GB, SWAP: 4GB, and Disk image size: 50+GB.


## How To
1. Configure

    To modify Govready-Q settings, you'll need to generate an `environment.json` to pass to the container.
    - `python run.py init` - This will generate `docker/environment.json` 
        * Note: If you don't do this, it will auto-generate one on start of stack
    - Simply change any value to modify your environment
        * A restart will be required if you modify the values between runs.
     
2. Start
    -  `python run.py dev`         : This will run + reuse previously built artifacts (database, files, etc)
    -  `python run.py dev --clean` : This will run + destroys your existing database and artifacts from previous runs
    
3. Stop
    -  `python run.py remove` : Stops the server but keeps persisted items (database volume, artifacts, etc)

4. Destroy DB
    -  `python run.py wipedb` : Destroys your existing database and artifacts from previous runs
    
4. Debugging
    - `docker attach govready_q_dev`
        - `crtl + c ` : This will detatch & kill the container and restart it
        - `ctrl + pq` : This will detatch
    - use ipdb as you normally would (https://gist.github.com/mono0926/6326015)
    
5. Connect to Container
    - `docker exec -it govready_q_dev /bin/bash`
    
    
## IDE Interpreter Steps

### Pycharm
#### Automated Sync via SSH Interpreter
- `File -> Settings -> Project -> Project Interpreter  -> Cog -> Add -> SSH Interpreter`
    - Host: `localhost`
    - Port: `2222`
    - User: `root`
    - Password: `root`
    - Interpreter: `/usr/src/app/dev_env/docker/remote_interpreter/python_env.sh`

### VIM
- `docker exec -it govready_q_dev /bin/bash` - Connect to the Django container directly to code.
- Code is synced in realtime.  Your code changes will be reflected on the host and will not be lost.


## FAQ

What runs every time in `python run.py dev`?
    
    - migrations : We need to apply migrations between branches
    - pip installs: We cannot assume libraries will remain static between branches
    
Docker is eating too much RAM.  What can I do?
    
    Windows
    - https://medium.com/@lewwybogus/how-to-stop-wsl2-from-hogging-all-your-ram-with-docker-d7846b9c5b37
    
How are my changes propagated to and from the container?      

    - In the "dev_env/docker/docker-compose.yaml" we have a volume set to "../..:/usr/src/app" under govready-q.  This sets up a bi-driectional mount.  
    - Any changes to the host will affect the container and any changes to the container will affect the host.
    
When do I rebuild the container?

    - This happens automatically.  If a change is detected in the Dockerfile, the next time you restart it will rebuild the container.
    
How do I see logs or interact with a debugger?

    - See "4. Debugging" under How To.  
    
How do I run management commands or interact with the container?

    - See "5. Connect to Container under How To.  
    
I just switched branches and my database is out of sync.  What do I do?

    - Exit the existing run by hitting "ctrl-c"
    - Run: python run.py dev --clean
    - This will clean up all artifacts and will wipe the existing database
    
