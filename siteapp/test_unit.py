# with help from
# http://www.programcreek.com/python/example/57384/test.test_support.EnvironmentVarGuard

from test.support import EnvironmentVarGuard
import unittest
from django.conf import settings
settings.configure()

class TestEnv(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentVarGuard()
        self.env.set('SECRET_KEY', 'xoxo')
        self.env.set(
            'DATABASE_URL',
             'bogus://myuser:mypass@myhost3:3306/my_database_name'
             )

    def test_secret_key(self):
        from siteapp import settings
        self.assertEqual(settings.SECRET_KEY,'xoxo')

    def test_db_url(self):
        from siteapp import settings
        self.assertEqual(
            settings.DATABASES['default']['HOST'],
            'myhost3'
            )
