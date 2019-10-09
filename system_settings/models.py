from django.db import models

class SystemSettings(models.Model):
  setting = models.CharField(max_length=200, unique=True)
  active = models.BooleanField(default=False)
  
  def __str__(self):
    return self.setting

  @classmethod
  def hide_registration(cls):
    return cls.objects.get(setting="hide_registration").active