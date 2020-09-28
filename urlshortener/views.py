from datetime import datetime
from importlib import import_module

from django.core import serializers
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.sessions.models import Session


from django.views import View

from urlshortener.forms import UrlForm
from urlshortener.models import Url, Statistics

engine = import_module(settings.SESSION_ENGINE)
SessionStore = engine.SessionStore


class UrlView(View):

    def get(self, request):
        if not request.session.session_key:
            request.session = SessionStore()
            request.session.create()
        form = UrlForm()
        current_user_urls = Url.objects.all().filter(session=request.session.session_key)
        return render(request, 'index.html', {
            'form': form,
            'root':  'http://127.0.0.1:8000/',
            'urls': current_user_urls
        })

    def post(self, request):
        form = UrlForm(request.POST)
        if form.is_valid():
            long_url = form.cleaned_data['long_url']
            session = Session.objects.get(pk=request.session.session_key)

            url = Url(long_url=long_url, session=session)
            url.save()
            return HttpResponseRedirect(self.request.path_info)
        return HttpResponse(status=400)


class UrlRoot(View):

    def get(self, request, url_hash):
        url = get_object_or_404(Url, url_hash=url_hash)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        referer = request.META.get('HTTP_REFERER')
        time = datetime.now()
        stats = Statistics(ip_address=ip, time=time, referer=referer, url=url)
        stats.save()
        return redirect(url.long_url)


class Stats(View):

    def get(self, request, url_id):
        stats = Statistics.objects.all().filter(url=url_id)
        data = serializers.serialize('json', stats)
        return JsonResponse(data, safe=False)
