#!/usr/bin/python3

# Josh set up the Django site with a common settings.py
# file that he uses across projects. It is parameterized
# by a file stored in local/environment.json. We will
# fill in some details given to us from the Cloud Foundry
# environment.

import os, json, sys
import dj_database_url

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT_FILE = os.path.join(APP_ROOT, "src/local/environment.json")

# Pull Cloud Foundry environment data.
VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
VCAP_APPLICATION = json.loads(os.environ['VCAP_APPLICATION'])

# Ensure the directory exists.
os.makedirs(os.path.dirname(ENVIRONMENT_FILE), exist_ok=True)

# Get initial info provided by the CF environment.
data = json.loads(os.environ['ENVIRONMENT_JSON'])

# Fill in additional general details.

# We are serving over HTTPS -- this affects some headers.
data["https"] = True

# We are serving static files via Django + whitenoise. The
# configuration is like a normal Django static configuration
# where static assets are generated in a separate storage
# area, and whitenoise will serve them from there.
data["static"] = "/home/vcap/staticfiles"

# Pull database settings from the DATABASE_URL environment
# variable, which is conveniently set by Cloud Foundry. It's also
# in VCAP_SERVICES['elephantsql'][0]['credentials']['uri']
data["db"] = dj_database_url.config(conn_max_age=60)

# Fill in Q-specific settings.

pass

# Save to where settings.py will see it.

with open(ENVIRONMENT_FILE, 'w') as f:
    json.dump(data, f, indent=2, sort_keys=True)
