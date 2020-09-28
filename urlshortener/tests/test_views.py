import json
from datetime import datetime
from importlib import import_module

from django.core import serializers
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from urlshortener.models import Url, Session, Statistics


class TestUrlView(TestCase):

    def setUp(self):
        engine = import_module(settings.SESSION_ENGINE)
        self.store = engine.SessionStore()
        self.store.save()

        self.user1_urls = [Url(long_url='https://www.youtube.com/watch?v=cSLAO7zxS2M',
                               session=Session(pk=self.client.session.session_key)),
                           Url(long_url='https://www.youtube.com/watch?v=bnVUHWCynig',
                               session=Session(pk=self.client.session.session_key))]
        self.user2_url = Url(long_url='https://www.youtube.com/watch?v=TRRfi3yOT8g',
                             session=Session(pk=self.store.session_key))
        for url in self.user1_urls:
            url.save()
        self.user2_url.save()

    def test_different_users(self):
        resp = self.client.get(reverse('url_view'))
        self.assertEqual(len(resp.context['urls']), 2)

    def test_valid_response(self):
        resp = self.client.get(reverse('url_view'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('urls' in resp.context)
        self.assertEqual(resp.context['root'], 'http://127.0.0.1:8000/')
        self.assertTrue(self.user1_urls[0] in resp.context['urls'])

    def test_post_success(self):
        data = {
            "long_url": 'https://www.youtube.com/watch?v=bnVUHWCynig&list=RDbnVUHWCynig&start_radio=1',
            "session": Session(pk=self.client.session.session_key)
        }
        resp = self.client.post(reverse('url_view'), data)
        self.assertEqual(resp.status_code, 302)

    def test_post_failure(self):
        data = {
            "long_url": 'not_an_url',
            "session": Session(pk=self.client.session.session_key)
        }
        resp = self.client.post(reverse('url_view'), data)
        self.assertEqual(resp.status_code, 400)


class TestUrlRootView(TestCase):
    def setUp(self):
        self.url = Url(long_url='https://www.youtube.com/watch?v=bnVUHWCynig',
                       session=Session(pk=self.client.session.session_key))
        self.url.save()

    def test_valid_redirect(self):
        resp = self.client.get('/{}/'.format(self.url.url_hash))
        self.assertEqual(resp.url, self.url.long_url)


class TestStatsView(TestCase):
    def setUp(self):
        self.url = Url(long_url='https://www.youtube.com/watch?v=bnVUHWCynig',
                       session=Session(pk=self.client.session.session_key))
        url2 = Url(long_url='https://www.youtube.com/watch?v=cSLAO7zxS2M',
                   session=Session(pk=self.client.session.session_key))
        self.url.save()
        url2.save()
        self.stats = [Statistics(ip_address='0.0.0.0', time=datetime.now(), referer='0.0.0.0', url=self.url),
                      Statistics(ip_address='172.16.0.0', time=datetime.now(), url=self.url),
                      Statistics(ip_address='172.16.0.0', time=datetime.now(), url=url2)]

        for stat in self.stats:
            stat.save()

    def test_get(self):
        resp = self.client.get('/stats/{}'.format(self.url.id))
        data = json.loads(resp.content)
        data = list(serializers.deserialize('json', data))
        self.assertEqual(len(data), 2)
