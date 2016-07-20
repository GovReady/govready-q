# These tests don't use
#   from django.test import SimpleTestCase
# because those tests insist on setting up a database, and when
# the engine is MySQL, then it tries to set up a MySQL DB.

# Instead, just do basic unittests and import the
# bits of Django's settings, and settings initialization
# to get going.

# Env var help from
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
             'mysql2://myuser:mypass@myhost:3306/my_database_name'
             )

    def test_secret_key(self):
        from siteapp import settings
        self.assertEqual(settings.SECRET_KEY,'xoxo')

    def test_db_url(self):
        from siteapp import settings
        self.assertEqual(
            settings.DATABASES['default']['HOST'],
            'myhost'
            )

    def test_db_name(self):
        from siteapp import settings
        self.assertEqual(
            settings.DATABASES['default']['NAME'],
            'my_database_name'
            )
