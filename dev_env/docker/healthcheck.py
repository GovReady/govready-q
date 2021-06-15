import os
import sys
from pathlib import Path

import requests

health_check_file = "/tmp/healthcheck"

if not(os.path.exists(health_check_file)):
    try:
        status_code = requests.get(
            'http://localhost:8000/').status_code
        if status_code != 200:
            sys.exit(1)
    except:

        sys.exit(1)

    Path(health_check_file).touch()
