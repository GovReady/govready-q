from django.conf import settings
from django.test import SimpleTestCase
from unittest import skip


# Would be nice to run this without setting up a DB
# see: http://stackoverflow.com/questions/5917587/django-unit-tests-without-a-db
# however, we can test settings w/o having to worry about mysql

class TestDefaultSettings(SimpleTestCase):
    def test_db_is_local(self):
        db_is = settings.DATABASES['default']['ENGINE']
        db_should_be = 'django.db.backends.sqlite3'
        self.assertEqual(db_is, db_should_be)

    def test_secret_key(self):
        self.assertIsNotNone(settings.SECRET_KEY)

    def test_misc_local_settings(self):
        self.assertEqual(settings.DEBUG, False)
#        self.assertEqual(settings.HTTPS, False)
#        self.assertEqual(settings.HOST, "localhost:8000")

    def test_misc_default_settings(self):
        self.assertEqual(settings.ALLOWED_HOSTS, ['*'])
        self.assertListEqual(settings.ADMINS,[])

    @skip("Skip CloudFormation tests until later")
    def test_only_cf_settings(self):
        skipTest("Not yet")
        self.assertIsNone(settings.USE_MEMCACHED)
        self.assertIsNone(settings.EMAIL)
        self.assertIsNone(settings.STATIC)

    def test_pre_cf_settings(self):
        self.assertRegexpMatches(
            settings.CACHES['default']['BACKEND'],
            'django.core.cache.backends.locmem.LocMemCache',
            "Default is to use LocMemCache, unless explictly using 'memcached'"
        )
        self.assertRegexpMatches(settings.EMAIL_SUBJECT_PREFIX, '[localhost:8000]')
        self.assertFalse(settings.SESSION_COOKIE_SECURE)
        self.assertIsNone(settings.STATIC_ROOT)
        self.assertEqual(settings.SITE_ROOT_URL, "http://localhost:8000")
