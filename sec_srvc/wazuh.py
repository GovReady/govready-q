import json

import requests
from sec_srvc.security_service import SecurityService
from base64 import b64encode
from urllib.parse import urlparse


class WazuhSecurityService(SecurityService):
    DESCRIPTION = {
        "name": "Example Security Service",
        "description": "Short description",
        "version": "2.1"
    }

    def setup(self, **kwargs):
        self.base_url = kwargs.pop('base_url')
        self.url_parts = urlparse(self.base_url)
        if not (self.url_parts.scheme and self.url_parts.netloc):
            raise Exception("Invalid base url")
        self.scheme = self.url_parts.scheme
        self.port = self.url_parts.port
        self.hostname = self.url_parts.hostname

    def authenticate(self, user=None, passwd=None):
        """Authenticate with service"""
        if user is None or passwd is None:
            self.error_msg = {"error": "Username and/or password not provided."}
            return
        login_url = f"{self.base_url}/security/user/authenticate"
        basic_auth = f"{user}:{passwd}".encode()
        headers = {'Authorization': f'Basic {b64encode(basic_auth).decode()}'}
        token = f'Bearer {self.get_response(login_url, headers)["data"]["token"]}'
        self.auth_dict = {"token": token}
        self.is_authenticated = True

    def extract_data(self, authentication, identifiers):
        """Extract data from Security Service using list of identifiers"""
        if not self.is_authenticated:
            raise Exception("User must be authenticated before making extraction request from Wazuh")

        identifier_ids = None
        if identifiers is not None:
            identifier_ids = identifiers.split(",")
        description = self.DESCRIPTION["description"]
        title = self.DESCRIPTION["name"]

        sar_list = []
        headers = dict(Authorization=self.auth_dict['token'])

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
                endpoint_result[
                    'url_link'] = f"{self.scheme}://{self.hostname}/app/wazuh#/overview/?tab=sca&agentId={identifer_id}"
                sar_list.append(endpoint_result)
            else:
                endpoint_result = None
        data = sar_list
        return data

    def transform_data(self, data, system_id=None, title=None, description=None, deployment_uuid=None):
        modified_items = data

        if deployment_uuid is not None:
            d_uuid_uuid = uuid.UUID(f'urn:uuid:{deployment_uuid}')
        else:
            d_uuid_uuid = None

        # TODO: update data time fields
        transformed_data = {'schema': 'GovReadySimpleSAR',
                            'version': '0.2',
                            "metadata": {
                                "deployment_uuid": f"{d_uuid_uuid}",
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

    def get_response(self, url, headers=None, verify=False):
        request_result = requests.get(url, headers=headers, verify=verify)
        if request_result.status_code == 200:
            return json.loads(request_result.content.decode())
        else:
            # TODO: better handling of response code; 401, 301, etc.
            raise Exception(f"Error obtaining response: {request_result.json()}")

    def load_data(self, data):
        return "Load data"
