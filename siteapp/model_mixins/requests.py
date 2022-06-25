from django.db import models
from django.http import JsonResponse

class RequestsModelMixin(models.Model):
    requests = models.ManyToManyField("siteapp.Request", blank=True, related_name="%(class)s")

    class Meta:
        abstract = True

    def add_requests(self, requests):
        if requests is None:
            requests = []
        elif isinstance(requests, str):
            requests = [requests]
        assert isinstance(requests, list)
        self.requests.add(*requests)

    def remove_requests(self, requests=None):
        if requests is None:
            requests = []
        elif isinstance(requests, str):
            requests = [requests]
        assert isinstance(requests, list)
        self.requests.remove(*requests)