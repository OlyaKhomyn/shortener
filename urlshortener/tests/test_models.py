from importlib import import_module

from django.conf import settings
from django.test import TestCase
from urlshortener.models import Url, Session


class TestUrlModel(TestCase):

    def setUp(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.url = Url(long_url='https://www.youtube.com/watch?v=cSLAO7zxS2M', session=Session(pk=store.session_key))
        self.url.save()

    def test_hash_url_was_saved(self):
        self.assertNotEqual(self.url.url_hash, None)
