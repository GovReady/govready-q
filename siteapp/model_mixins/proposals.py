from django.db import models
from django.http import JsonResponse

class ProposalModelMixin(models.Model):
    proposals = models.ManyToManyField("siteapp.Proposal", blank=True, related_name="%(class)s")

    class Meta:
        abstract = True

    def add_proposals(self, proposals):
        if proposals is None:
            proposals = []
        elif isinstance(proposals, str):
            proposals = [proposals]
        assert isinstance(proposals, list)
        self.proposals.add(*proposals)

    def remove_proposals(self, proposals=None):
        if proposals is None:
            proposals = []
        elif isinstance(proposals, str):
            proposals = [proposals]
        assert isinstance(proposals, list)
        self.proposals.remove(*proposals)