from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import request, parse

import os
import platform
import re
import signal
import sys
from base64 import b64encode
import requests
import urllib3

import json
import random
import uuid

class SecurityService:

    def description(self):
        description = {
            "name": "Example Security Service",
            "description": "Short description",
            "version": "2.1"
        }
        return description

    def setup(self, base_url):
        self.base_url = base_url
        return True

    def get_response(self, url, headers=None, verify=False):
        request_result = requests.get(url, headers=headers, verify=verify)
        if request_result.status_code == 200:
            return json.loads(request_result.content.decode())
        else:
            # TODO: better handling of response code; 401, 301, etc.
            raise Exception(f"Error obtaining response: {request_result.json()}")

    def authenticate(self, user=None, passwd=None):
        """Authenticate with service"""

        if user == None or passwd == None:
            self.srvc_auth = { "authenticated": False,
                "token": None,
                "error": "Username and/or password not provided."
            }
            return self.srvc_auth
        self.login_url = f"{self.base_url}/security/user/authenticate"
        basic_auth = f"{user}:{passwd}".encode()
        headers = {'Authorization': f'Basic {b64encode(basic_auth).decode()}'}
        token = f'Bearer {self.get_response(self.login_url, headers)["data"]["token"]}'
        self.srvc_auth = { "authenticated": True,
            "token": token,
            "error": None
        }
        return self.srvc_auth

    def extract_data(self, authentication, identifiers):
        """Extract data from Security Service using list of identifiers"""

        identifier_ids = None
        if identifiers is not None:
            identifier_ids = identifiers.split(",")
        description = self.description()["description"]
        title = self.description()["name"]

        sar_list = []
        headers = {}

        # Authorize
        if self.srvc_auth and self.srvc_auth['authenticated']:
            headers['Authorization'] = self.srvc_auth['token']
        else:
            # TODO: Handle no authentication on attempt to extract data
            pass

        # Extract data
        for identifer_id in identifier_ids:
            # Retrieve Wazuh SCA scan for each agent
            endpoint = f'/sca/{identifer_id}?pretty=true'
            response = self.get_response(self.base_url + endpoint, headers)

            # Enhance data
            # TODO: Should this be in transform?
            if len(response["data"]["affected_items"]) == 1:
                endpoint_result = response["data"]["affected_items"][0]
                # Enhance agent result
                endpoint_result['agent'] = identifer_id
                endpoint_result['ip_address'] = None
                endpoint_result['url_link'] = f"{PROTOCOL}://{HOST}/app/wazuh#/overview/?tab=sca&agentId={identifer_id}"
                sar_list.append(endpoint_result)
            else:
                endpoint_result = None
        data = sar_list
        return data

    def transform_data(self, data, system_id=None, title=None, description=None, deployment_uuid=None):
        modified_items = data

        # TODO: update data time fields
        transformed_data = {'schema': 'GovReadySimpleSAR',
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
           'sar': modified_items
        }
        return transformed_data

    def load_data(self, data):
        return "Load data"
