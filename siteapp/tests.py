from django.conf import settings
from django.test import SimpleTestCase

# Would be nice to run this without setting up a DB
# see: http://stackoverflow.com/questions/5917587/django-unit-tests-without-a-db
# however, we can test settings w/o having to worry about mysql

class DefaultSettings(SimpleTestCase):
    def test_db_is_local(self):
        db_is = settings.DATABASES['default']['ENGINE']
        db_should_be = 'django.db.backends.sqlite3'
        self.assertEqual(db_is, db_should_be)

    def test_secret_key(self):
        self.assertIsNotNone(settings.SECRET_KEY)

    def test_misc_local_settings(self):
        self.assertEqual(settings.DEBUG, False)
        self.assertEqual(settings.HTTPS, False)
        self.assertEqual(settings.HOST, "localhost:8000")

    def test_misc_default_settings(self):
        print("AH: %s", settings.ALLOWED_HOSTS)
        self.assertEqual(settings.ALLOWED_HOSTS, "localhost")
        self.assertEmpty(settings.ADMINS)
        self.assertNone(settings.USE_MEMCACHED)
        self.assertNone(settings.EMAIL)
        self.assertNone(settings.STATIC)
