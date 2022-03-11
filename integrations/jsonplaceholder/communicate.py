import requests
import json
from base64 import b64encode
from urllib.parse import urlparse
from integrations.utils.integration import Communication
from integrations.models import Integration, Endpoint


class JsonplaceholderCommunication(Communication):
    
    DESCRIPTION = {
        "name": "Jsonplaceholder",
        "description": "Test API Jsonplaceholder",
        "version": "0.1",
        "base_url": "https://jsonplaceholder.typicode.com",
        "personal_access_token": None
    }

    # integrations record config value:
    # {
    #     "base_url": "http://jsonplaceholder.typicode.com",
    #     "personal_access_token": null
    # }

    def __init__(self, **kwargs):
        assert self.DESCRIPTION, "Developer must assign a description dict"
        self.__is_authenticated = False
        self.error_msg = {}
        self.auth_dict = {}
        self.data = None
        self.status_code = None
        self.base_url = self.DESCRIPTION['base_url']

    # def identify(self):
    #     """Identify which Communication subclass"""
    #     identity_str = f"This is {self.DESCRIPTION['name']} version {self.DESCRIPTION['version']}"
    #     print(identity_str)
    #     return identity_str

    def setup(self, **kwargs):
        pass

    def get_response(self, endpoint, headers=None, verify=False):
        response = requests.get(f"{self.base_url}{endpoint}")
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
