import requests
import json
from base64 import b64encode
from urllib.parse import urlparse
from integrations.utils.integration import Communication
from integrations.models import Integration, Endpoint


class GithubCommunication(Communication):
    
    DESCRIPTION = {
        "name": "GitHub",
        "description": "GitHub API Service",
        "version": "0.1",
        "integration_db_record": False,
        "mock": {
            "base_url": "http:/localhost:9003",
            "personal_access_token": None
        }
    }

    def __init__(self, **kwargs):
        assert self.DESCRIPTION, "Developer must assign a description dict"
        self.__is_authenticated = False
        self.error_msg = {}
        self.auth_dict = {}
        self.data = None
        self.base_url = "https://github.com/api"

    def identify(self):
        """Identify which Communication subclass"""
        identity_str = f"This is {self.DESCRIPTION['name']} version {self.DESCRIPTION['version']}"
        print(identity_str)
        return identity_str

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
