from django.test import TestCase
from django.conf import settings


class SettingsTests(TestCase):
    def test_db_is_local(self):
        db_is = settings.DATABASES['default']['ENGINE']
        db_should_be = 'django.db.backends.sqlite3'

        self.assertEqual(db_is, db_should_be)
