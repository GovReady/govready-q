import multiprocessing
command = 'gunicorn'
pythonpath = '/home/govready-q/govready-q/venv/bin'
# Extend time out to 10 min to import large project, OSCAL files
timeout = 500
# serve GovReady-Q locally on server to use nginx as a reverse proxy
bind = 'localhost:8000'
# Only set workers higher than 1 if `secret-key` is defined in local/environment.json
# If secret-key is auto-generated instead of shared, key will not be shared with gunicorn
# which causes the login session for users to drop as soon as they hit a different worker
workers = multiprocessing.cpu_count() * 2 + 1 # recommended for high-traffic sites
# workers = 1
worker_class = 'gevent'
user = 'govready-q'
keepalive = 10

# start command
# gunicorn -c /home/govready-q/govready-q/local/gunicorn.conf.py siteapp.wsgi
