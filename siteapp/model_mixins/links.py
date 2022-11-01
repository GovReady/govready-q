from django.db import models
from django.http import JsonResponse

class LinkModelMixin(models.Model):
    links = models.ManyToManyField("controls.Link", blank=True, related_name="%(class)s")

    class Meta:
        abstract = True

    def add_prop(self, links):
        if links is None:
            links = []
        elif isinstance(links, str):
            links = [links]
        assert isinstance(links, list)
        self.links.add(*links)

    def remove_prop(self, links=None):
        if links is None:
            links = []
        elif isinstance(links, str):
            links = [links]
        assert isinstance(links, list)
        self.links.remove(*links)