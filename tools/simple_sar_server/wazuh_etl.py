#!/usr/bin/env python3

########################################################
#
# A simple middleware to submit a scan report
# assessment results
#
# Usage:
#   python wazuh_etl.py <apikey> <sar_service_url> [-s <system_id>] [-d <deployment_uuid>]
#
# Example:
#   python wazuh_etl.py eCXZbZwmBrtD5hgrJ8ptmJfvDA5vlDcc wazuh-1.govready.com -s 132 -d f7b0d84e-397c-43de-bb1f-421afa467993
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
from base64 import b64encode
import requests
import urllib3

# JSON and other data handling
import json
import random
import uuid

# Default constants
GOVREADYHOST = "http://localhost:8000"
PROTOCOL = 'https'
HOST = 'wazuh-1.govready.com'
PORT = '55000'
USER = 'wazuh'
PASSWORD = 'wazuh'
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


# Functions
def get_response(url, headers, verify=False):
    """Get API result"""
    request_result = requests.get(url, headers=headers, verify=verify)

    if request_result.status_code == 200:
        return json.loads(request_result.content.decode())
    else:
        raise Exception(f"Error obtaining response: {request_result.json()}")

# Commandline arguments
@click.command()
@click.argument('apikey', default=None)
@click.argument('sar_url', default=None)
@click.option('-s', default=None)
@click.option('-d', default=None)
@click.option('--agents', default=None)
def main(apikey,sar_url, s, d, agents):

    # Set system_id, deployment_uuid
    system_id = s
    deployment_uuid = d
    agent_ids = None
    if agents is not None:
        agent_ids = agents.split(",")
    print("agent_ids", agent_ids)
    description = "Wazuh regular scan"
    title = "Wazuh SCA scan"

    # Get SAR from SAR Service
    print(SPACER)
    print(f"Retrieving SAR from service: {sar_url}")

    sar_list = []
    # Retrieve Wazuh SCA scan for each agent
    for agent_id in agent_ids:
        # Variables
        endpoint = f'/sca/{agent_id}?pretty=true'
        base_url = f"{PROTOCOL}://{HOST}:{PORT}"
        login_url = f"{base_url}/security/user/authenticate"
        basic_auth = f"{USER}:{PASSWORD}".encode()
        headers = {'Authorization': f'Basic {b64encode(basic_auth).decode()}'}
        print(json.dumps(get_response(login_url, headers), indent=4, sort_keys=True))
        headers['Authorization'] = f'Bearer {get_response(login_url, headers)["data"]["token"]}'

        #Request
        response = get_response(base_url + endpoint, headers)

        # print(json.dumps(response, indent=4, sort_keys=True))
        if len(response["data"]["affected_items"]) == 1:
            agent_result = response["data"]["affected_items"][0]
            # Enhance agent result
            agent_result['agent'] = agent_id
            agent_result['ip_address'] = None
            agent_result['url_link'] = f"{PROTOCOL}://{HOST}/app/wazuh#/overview/?tab=sca&agentId={agent_id}"
            sar_list.append(agent_result)
        else:
            agent_result = None
        print("agent_result from wazuh",json.dumps(agent_result, indent=4, sort_keys=True))

    # Build SAR object
    sar = {'schema': 'GovReadySimpleSAR',
           'version': '0.2',
           "metadata": {
                "deployment_uuid": f"{deployment_uuid}",
                "description": f"{description}",
                "last-modified": "dateTime-with-timezone",
                "published": "dateTime-with-timezone",
                "schema": "GovReadySimpleSAR",
                "system_id": f"{system_id}",
                "title": f"{title}",
                "version": "0.2"
            },
           'sar':sar_list
    }

    print("sar", json.dumps(sar, indent=4, sort_keys=True))

    # Build query
    url_query = endpoint

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
