from django.db import models
from django.http import JsonResponse

class TagModelMixin(models.Model):
    tags = models.ManyToManyField("siteapp.Tag", blank=True, related_name="%(class)s")

    def add_tags(self, tags=None):
        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]
        assert isinstance(tags, list)
        self.tags.add(*tags)

    def remove_tags(self, tags=None):
        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]
        assert isinstance(tags, list)
        self.tags.remove(*tags)

    class Meta:
        abstract = True

class TagView:

    @staticmethod
    def add_tag(request, obj_id, tag_id, model):
        from siteapp.models import Tag
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"Tag does not exist"}, status=404)
        model.objects.get(id=obj_id).add_tags(tags=[tag])
        return JsonResponse({"status": "ok", "data": tag.serialize()}, status=201)

    @staticmethod
    def remove_tag(request, obj_id, tag_id, model):
        from siteapp.models import Tag
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"Tag does not exist"}, status=404)
        model.objects.get(id=obj_id).remove_tags(tags=[tag])
        return JsonResponse({"status": "ok"})

    @staticmethod
    def list_tags(request, obj_id, model):
        tags = []
        for tag in model.objects.get(id=obj_id).tags.all().iterator():
            tags.append(tag.serialize())
        return JsonResponse({"status": "ok", "data": tags})

def build_tag_urls(path_prefix, model):
    from django.conf.urls import url
    return [
        url(rf'{path_prefix}tags/(\d+)/_add$', lambda *args, **kwargs: TagView.add_tag(*args, model, **kwargs),
            name=f"add_tag_to_{model.__name__.lower()}"),
        url(rf'{path_prefix}tags/(\d+)/_remove$',
            lambda *args, **kwargs: TagView.remove_tag(*args, model, **kwargs),
            name=f"remove_tag_from_{model.__name__.lower()}"),
        url(rf'{path_prefix}tags/$', lambda *args, **kwargs: TagView.list_tags(*args, model, **kwargs),
            name=f"list_element_{model.__name__.lower()}"),
    ]
