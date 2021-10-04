from django.db import models


class BaseModel(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  #  TODO - change in SPA

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True, db_index=True)

    objects = models.Manager()

    class Meta:
        abstract = True
