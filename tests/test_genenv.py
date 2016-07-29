import unittest, os
from test.support import EnvironmentVarGuard
from siteapp import genenv

class TestFullEnv(unittest.TestCase):
    # in order of appearance in settings.py
    output_env = {
        'secret-key': 'xoxox',
        'debug': True,
        'host': 'localhost:8000',
        'https': True,
        'admins': ['aaa','bbbb', 'cc'],
        'memcached': True,
        # for settings_application.py
        'modules': 'some/path/for/modules',
        'govready_cms_api_auth': 'https://mycms.com/'
    }
    output_email = {
          'host': 'mailhost',
          'port': 465,
          'user': 'eric',
          'pw': 'allman'
    }
    output_db = {
        'USER': 'myuser',
        'NAME': 'my_database_name',
        'HOST': 'myhost',
        'PASSWORD': 'mypass',
        'PORT': 3306,
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 60,
    }

    def setUp(self):
        os.environ['SECRET_KEY'] = 'xoxox'
        os.environ['DEBUG'] = 'True'
        os.environ['HOST'] = 'localhost:8000'
        os.environ['HTTPS'] = 'True'
        os.environ['ADMINS'] = 'aaa:bbbb:cc'
        os.environ['MEMCACHED'] = 'true'
        os.environ['STATIC'] = 'true'
        os.environ['MODULES_PATH'] = 'some/path/for/modules'
        os.environ['GOVREADY_CMS_API_AUTH'] = 'https://mycms.com/'
        os.environ['EMAIL'] = 'email://eric:allman@mailhost:465'
        os.environ['DATABASE_URL'] = 'mysql://myuser:mypass@myhost:3306/my_database_name'

    def test_populate_static(self):
        self.assertRegex(genenv.populate_static(),
                         'govready-q/siteapp/staticfiles$')

    def test_populate_env(self):
        e = genenv.populate_env(genenv.env_dict())
        self.assertDictEqual(e, self.output_env)

    def test_populate_email(self):
        self.assertDictEqual(genenv.populate_email(), self.output_email )

    def test_populate_db(self):
        self.assertDictEqual(genenv.populate_db(), self.output_db)

class TestEmptyEnv(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentVarGuard()
        self.env.clear()

    def test_populate_static(self):
        self.assertIsNone(genenv.populate_static())

    def test_populate_all(self):
        self.assertDictEqual(genenv.all(), {})
