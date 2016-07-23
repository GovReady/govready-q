import unittest
from test.support import EnvironmentVarGuard
from deployment import genenv


class TestFullEnv(unittest.TestCase):
    # in order of appearance in settings.py
    output_env = {
        'secret-key': 'xoxox',
        'debug': True,
        'host': 'localhost:8000',
        'https': True,
        'admins': ['aaa','bbbb', 'cc'],
        'memcached': True,
        'static': '/path/to/static',
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
        self.env = EnvironmentVarGuard()
        self.env.set('SECRET_KEY', 'xoxox')
        self.env.set('DEBUG', 'True')
        self.env.set('HOST', 'localhost:8000')
        self.env.set('HTTPS', 'True')
        self.env.set('ADMINS', 'aaa:bbbb:cc')
        self.env.set('MEMCACHED', 'true')
        self.env.set('STATIC', '/path/to/static')

        self.env.set('MODULES_PATH', 'some/path/for/modules')
        self.env.set('GOVREADY_CMS_API_AUTH', 'https://mycms.com/')
        self.env.set('EMAIL', 'email://eric:allman@mailhost:465')

        self.env.set('DATABASE_URL',
                     'mysql://myuser:mypass@myhost:3306/my_database_name')

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

    def test_populate_all(self):
        self.assertDictEqual(genenv.all(), {})
