from django import forms

from urlshortener.models import Url


class UrlForm(forms.ModelForm):

    class Meta:
        model = Url
        fields = ('long_url',)
