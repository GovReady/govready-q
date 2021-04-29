#!/usr/bin/env python3

########################################################
#
# A simple middleware to submit a scan report
# assessment results
#
# Usage:
#   python sar_etl.py <apikey> <sar_service_url> [-s <system_id>] [-d <deployment_uuid>]
#
# Example:
#   python sar_etl.py eCXZbZwmBrtD5hgrJ8ptmJfvDA5vlDcc http://localhost:8888/ -s 132 -d f7b0d84e-397c-43de-bb1f-421afa467993
# Accessing:
#   curl localhost:8888
#
#
# Optional arguments:
#   -h, --help             show this help message and exit
#   -d                     deployment uuid
#   -s                     system id
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
@click.option('-s', default=None)
@click.option('-d', default=None)
def main(apikey,sar_url, s, d):

    # Set system_id, deployment_uuid
    system_id = s
    deployment_uuid = d
    # deployment_id = 226

    #build query
    url_query = f"?system_id={system_id}&deployment_uuid={deployment_uuid}"

    # Get SAR from SAR Service
    print(SPACER)
    print(f"Retrieving SAR from service: {sar_url}{url_query}")
    handler = request.urlopen(f"{sar_url}{url_query}")
    sar = json.loads(handler.read().decode( 'utf-8' ));
    # print(sar)

    system_id = sar["metadata"]["system_id"]

    if deployment_uuid is not None:
        d_uuid_uuid = uuid.UUID(f'urn:uuid:{deployment_uuid}')
    else:
        d_uuid_uuid = None
    # Submit sar data to GovReady-q API
    data = {
        "system_id": system_id,
        "deployment_uuid": d_uuid_uuid,
        "sar_json": json.dumps(sar)
    }

    from pprint import pprint
    # pprint(data)
    data = bytes( parse.urlencode( data ).encode() )

    # POST retrieved SAR data to GovReady-Q via API
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

    print(SPACER)
    print(f"Posting retrieved SAR to: {gr_api_url}")

    # Post to GovReady
    req = request.Request( gr_api_url, data=data, headers=headers, method="POST" );
    response = request.urlopen(req)
    response.read()

    print(SPACER)
    print(response.read())

if __name__ == "__main__":
    main()
