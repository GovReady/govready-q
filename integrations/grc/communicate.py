import requests
import json
from base64 import b64encode
from urllib.parse import urlparse
from django.shortcuts import get_object_or_404
from integrations.utils.integration import Communication
from integrations.models import Integration, Endpoint


class GRCCommunication(Communication):
    
    DESCRIPTION = {
        "name": "grc",
        "description": "GRC API Service",
        "version": "0.3",
        "integration_db_record": True,
        "mock": {
            "base_url": "http:/localhost:9022",
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

    def get_response(self, endpoint, headers=None, params=None, verify=False, timeout=20):
        """Send request using GET"""

        # PAT for mock service is 'FAD619'
        headers={
            "accept":"application/json;odata.metadata=minimal;odata.streaming=true",
            "Authorization": f"Bearer {self.personal_access_token}"
        }
        # get response
        if self.ssl_verify:
            verify = self.ssl_verify
        try:
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers, verify=verify, timeout=10)
            self.status_code = response.status_code
        except:
            response = None
            self.status_code = None
        if self.status_code == 200:
            self.data = response.json()
        elif self.status_code == 404:
            print("404 - page not found")
            self.data = {}
        else:
            # problem connecting
            print("500 - Remote service unavailable or returned error. Is remote service running?")
            self.data = {"message": "Remote service unavailable or returned error. Is remote service running?"} 
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
