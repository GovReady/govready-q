from django.db import models

class SystemSettings(models.Model):
  """Model for various system settings for install of GovReady"""

  setting = models.CharField(max_length=200, unique=True)
  active = models.BooleanField(default=False)

  def __str__(self):
    return self.setting

  @classmethod
  def hide_registration(cls):
    return cls.objects.get(setting="hide_registration").active

  @classmethod
  def enable_experimental_opencontrol(cls):
    return cls.objects.get(setting="enable_experimental_opencontrol").active

  @classmethod
  def enable_experimental_oscal(cls):
    return cls.objects.get(setting="enable_experimental_oscal").active
