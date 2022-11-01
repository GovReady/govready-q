from django.db import models
from django.http import JsonResponse

class PropModelMixin(models.Model):
    props = models.ManyToManyField("controls.Prop", blank=True, related_name="%(class)s")

    class Meta:
        abstract = True

    def add_prop(self, props):
        if props is None:
            props = []
        elif isinstance(props, str):
            props = [props]
        assert isinstance(props, list)
        self.props.add(*props)

    def remove_prop(self, props=None):
        if props is None:
            props = []
        elif isinstance(props, str):
            props = [props]
        assert isinstance(props, list)
        self.props.remove(*props)