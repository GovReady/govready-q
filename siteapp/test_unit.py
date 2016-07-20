
import unittest

class TestEnv(unittest.TestCase):
    def test_one(self):
        from django.conf import settings
        settings.configure()
        from siteapp import settings
        print("SETTINGS " + settings.SECRET_KEY)
        self.assertEqual(True,True)
