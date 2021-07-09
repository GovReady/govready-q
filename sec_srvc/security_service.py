
class SecurityService:
    DESCRIPTION = {}

    def __init__(self, **kwargs):
        assert self.DESCRIPTION, "Developer must assign a description dict"
        self.__is_authenticated = False
        self.error_msg = {}
        self.auth_dict = {}
        self.data = None
        self.base_url = None

    def setup(self, **kwargs):
        raise NotImplementedError()

    def get_response(self, url, headers=None, verify=False):
        raise NotImplementedError()

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
