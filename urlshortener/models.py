from django.db import models
from hashlib import md5
from django.contrib.sessions.models import Session


class Url(models.Model):
    long_url = models.URLField(unique=True)
    url_hash = models.URLField(unique=True)
    session = models.ForeignKey('sessions.Session', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.id:
            self.url_hash = md5(self.long_url.encode()).hexdigest()[:10]

        return super().save(*args, **kwargs)


class Statistics(models.Model):
    ip_address = models.GenericIPAddressField()
    time = models.DateTimeField()
    referer = models.URLField(null=True)
    url = models.ForeignKey(Url, on_delete=models.CASCADE)

