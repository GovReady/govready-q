import json
import os
import subprocess
import sys
from abc import ABC
from urllib.parse import urlparse


class HelperMixin:

    def __init__(self):
        pass

    def create_secret(self):
        import secrets
        alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(alphabet) for i in range(50))

    def check_if_valid_uri(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False

    def cleanup(self):
        raise NotImplementedError()

    def on_complete(self):
        raise NotImplementedError()


class Communication(HelperMixin, ABC):

    DESCRIPTION = {
        "name": "abstract class",
        "description": "Abstract integration class",
        "version": "0.0",
        "integration_db_record": False,
        "mock": {
            "base_url": "http:/localhost:9001",
            "personal_access_token": None
        }
    }

    def __init__(self, **kwargs):
        self.integration_name = self.DESCRIPTION['name']

        if self.DESCRIPTION['integration_db_record']:
            self.integration = get_object_or_404(Integration, name=self.integration_name)
            self.description = self.integration.description
            self.config = self.integration.config
            self.base_url = self.config['base_url']
        else:
            self.description = self.DESCRIPTION['description']
            self.personal_access_token = self.config['personal_access_token']
        self.__is_authenticated = False
        self.error_msg = {}
        self.auth_dict = {}
        self.version = self.DESCRIPTION['version']
        self.data = None

    def identify(self):
        """Identify which Communication subclass"""
        identity_str = f"This is {self.DESCRIPTION['name']} version {self.DESCRIPTION['version']}"
        print(identity_str)
        return identity_str

    def setup(self, **kwargs):
        raise NotImplementedError()

    def msg_missing_configuration(self):
        """Message that the integration is not properly configured"""

        msg = f"The {self.integration_name} integration is not fully configured. The problem could be no database record or no integration subclass."

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
        raise NotImplementedError()

    @property
    def is_authenticated(self):
        return self.__is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value):
        self.__is_authenticated = value

    def extract_data(self, authentication, identifiers):
        """Extract data from Security Service using list of identifiers"""
        raise NotImplementedError()

    def transform_data(self, data, system_id=None, title=None, description=None, deployment_uuid=None):
        raise NotImplementedError()

    def load_data(self, data):
        raise NotImplementedError()
