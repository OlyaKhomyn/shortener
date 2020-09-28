from django.test import TestCase
from urlshortener.forms import UrlForm


class FormTest(TestCase):

    def test_valid_form(self):
        data = {'long_url': 'https://www.youtube.com/watch?v=cSLAO7zxS2M'}
        form = UrlForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_null(self):
        data = {'long_url': ''}
        form = UrlForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_url(self):
        data = {'long_url': 'not_an_url'}
        form = UrlForm(data=data)
        self.assertFalse(form.is_valid())
