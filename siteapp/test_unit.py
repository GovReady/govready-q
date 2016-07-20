# with help from
# http://www.programcreek.com/python/example/57384/test.test_support.EnvironmentVarGuard

from test.support import EnvironmentVarGuard
import unittest

class TestEnv(unittest.TestCase):
    def test_secret_key(self):
        with EnvironmentVarGuard() as environ:
            environ['SECRET_KEY'] = 'xoxo'
            from django.conf import settings
            settings.configure()
            from siteapp import settings
            
            self.assertEqual(settings.SECRET_KEY,'xoxo')
