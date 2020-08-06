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
    return cls.objects.get(setting="enable_experimental_opencontrol").active

class Support(models.Model):
  """Model for support infomation for support page for install of GovReady"""

  support_email = models.EmailField(max_length=254, unique=False, blank=True, null=True, help_text="Support email address")
  support_phone = models.CharField(max_length=24, unique=False, blank=True, null=True, help_text="Support phone number")
  support_text = models.TextField(unique=False, blank=True, null=True, help_text="Support desription at top of page")
  support_url = models.URLField(max_length=200, unique=False, blank=True, null=True, help_text="Support url")

  def __str__(self):
    return "Support information"
