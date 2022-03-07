import requests
import json
from base64 import b64encode
from urllib.parse import urlparse
from integrations.utils.integration import Communication


class CSAMCommunication(Communication):
    
    DESCRIPTION = {
        "name": "CSAM",
        "description": "CSAM API Service",
        "version": "0.1",
        "base_url": "http://localhost:9002",
    }

    def __init__(self, **kwargs):
        assert self.DESCRIPTION, "Developer must assign a description dict"
        self.__is_authenticated = False
        self.error_msg = {}
        self.auth_dict = {}
        self.data = None
        self.base_url = self.DESCRIPTION['base_url']

    # def identify(self):
    #     """Identify which Communication subclass"""
    #     super().identify()

    def setup(self, **kwargs):
        pass

    def get_response(self, endpoint, headers=None, verify=False):
        # set headers
        self.PAT_TOKEN = "FAD619BF4A06903215E59A626XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        # accept_header = f'accept: application/json;odata.metadata=minimal;odata.streaming=true'
        # auth_header = f'Authorization: Bearer {self.PAT_TOKEN}'
        #-H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' 
        #-H 'Authorization: Bearer FAD619BF4A06903215E59A626XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        headers={"accept":"application/json;odata.metadata=minimal;odata.streaming=true",
         "Authorization": f"Bearer {self.PAT_TOKEN}"
        }
        # get response
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
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
