import requests
import json
from base64 import b64encode
from urllib.parse import urlparse
from django.shortcuts import get_object_or_404
from integrations.utils.integration import Communication
from integrations.models import Integration, Endpoint


class CSAMCommunication(Communication):
    
    DESCRIPTION = {
        "name": "csam",
        "description": "CSAM API Service",
        "version": "0.3",
        "integration_db_record": True,
        "mock": {
            "base_url": "http:/localhost:9002",
            "personal_access_token": "FAD619"
        }
    }

    def __init__(self, **kwargs):
        self.status_code = None
        self.integration_name = self.DESCRIPTION['name']
        self.integration = get_object_or_404(Integration, name=self.integration_name)
        self.description = self.integration.description
        self.config = self.integration.config
        self.base_url = self.config['base_url']
        self.ssl_verify = self.config.get('ssl_verify', False) 
        self.personal_access_token = self.config['personal_access_token']
        self.__is_authenticated = False
        self.error_msg = {}
        self.auth_dict = {}
        self.data = None

    # def identify(self):
    #     """Identify which Communication subclass"""
    #     super().identify()

    def setup(self, **kwargs):
        pass

    def get_response(self, endpoint, headers=None, params=None, verify=False):
        """Send request using GET"""

        # PAT for mock service is 'FAD619'
        headers={
            "accept":"application/json;odata.metadata=minimal;odata.streaming=true",
            "Authorization": f"Bearer {self.personal_access_token}"
        }
        print(f"get_response headers, {headers}")
        print(f"get_response base_url: {self.base_url}{endpoint}")
        # get response
        if self.ssl_verify:
            verify = self.ssl_verify
        print(f"request info: ========= {self.base_url}{endpoint}")
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers, verify=verify)
        print(f"get_response, response {response}")
        self.status_code = response.status_code
        if self.status_code == 200:
            self.data = response.json()
        elif self.status_code == 404:
            print("404 - page not found")
        else:
            pass
        return self.data

    def post_response(self, endpoint, data=None, params=None, verify=False):
        """Send request using POST"""

        headers = {
            "accept": "application/json;odata.metadata=minimal;odata.streaming=true",
            "Authorization": f"Bearer {self.personal_access_token}"
        }
        # get response
        if self.ssl_verify:
            verify = self.ssl_verify
        response = requests.post(f"{self.base_url}{endpoint}", headers=headers, data=data, verify=verify)
        self.status_code = response.status_code
        if self.status_code == 200:
            self.data = response.json()
        elif self.status_code == 404:
            print("404 - page not found")
        else:
            pass
        return self.data

    def authenticate(self, user=None, passwd=None):
        """Authenticate with service"""
        pass

    @property
    def is_authenticated(self):
        return self.__is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value):
        self.__is_authenticated = value

    def extract_data(self, authentication, identifiers):
        """Extract data"""
        pass

    def transform_data(self, data, system_id=None, title=None, description=None, deployment_uuid=None):
        pass

    def load_data(self, data):
        pass
