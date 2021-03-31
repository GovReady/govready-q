#!/usr/bin/env python3

########################################################
#
# A simple middleware to submit a scan report
# assessment results
#
# Usage:
#   python sar_etl.py <apikey> <sar_service_url>
#
# Example:
#   python sar_etl.py eCXZbZwmBrtD5hgrJ8ptmJfvDA5vlDcc http://localhost:8888/
# Accessing:
#   curl localhost:8888
#
# Usage: install.py [--help] [--non-interactive] [--verbose]
#
# Optional arguments:
#   -h, --help             show this help message and exit
#   -a, --apikey           api_key for authenticating to GovReady-Q
#   -t, --sar_url          URL of SAR service
#   -v, --verbose          output more information
#
################################################################

# Parse command-line arguments
import click

# Web stuff
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import request, parse

# System stuff
import os
import platform
import re
import signal
import sys

# JSON and other data handling
import json
import random
import uuid

# Default constants
GOVREADYHOST = "http://localhost:8000"
SPACER = "\n====\n"

# Gracefully exit on control-C
signal.signal(signal.SIGINT, lambda signal_number, current_stack_frame: sys.exit(0))

# Define a fatal error handler
class FatalError(Exception):
    pass

# Define a halted error handler
class HaltedError(Exception):
    pass

# Define a non-zero return code error handler
class ReturncodeNonZeroError(Exception):
    def __init__(self, completed_process, msg=None):
        if msg is None:
            # default message if none set
            msg = "An external program or script returned an error."
        super(ReturncodeNonZeroError, self).__init__(msg)
        self.completed_process = completed_process

# Commandline arguments
@click.command()
@click.argument('apikey', default=None)
@click.argument('sar_url', default=None)
def main(apikey,sar_url):
    # print("sar_url",sar_url, apikey)

    # Set parameters
    # apikey = get_args()
    # Set system_id, deployment_id
    system_id = 132
    deployment_id = 226

    # Get SAR from SAR Service
    handler = request.urlopen(sar_url);
    sar = json.loads(handler.read().decode( 'utf-8' ));
    # print(sar)

    # Submit sar data to GovReady-q API
    data = {
        "system_id": sar["system_id"],
        "deployment_id": deployment_id,
        "sar_json": json.dumps(sar)
    }
    from pprint import pprint
    data = bytes( parse.urlencode( data ).encode() )

    """
    curl --header "Authorization: <api_key>" \
    -F "name=test_sar_api" \
    -F "system_id=86" \
    -F "deployment_id=23" \
    -F "data=@controls/data/test_data/test_sar1.json" \
    localhost:8000/api/v1/systems/86/assessment/new

    """

    # Prepare headers
    headers = {
                "Authorization": f"{apikey}"
              }

    # Set GovReady URL
    gr_api_url = f"{GOVREADYHOST}/api/v1/systems/{system_id}/assessment/new"

    # Post to GovReady
    req = request.Request( gr_api_url, data=data, headers=headers, method="POST" );
    response = request.urlopen(req)
    response.read()
    print(response.read())

if __name__ == "__main__":
    main()
