from django.db import models

# This is just a bare minimum for demo. Needs to be elaborated upon. Classified intentionally left out because it has complicated implications.


class Classification(models.Model):
    CLASS_STATUS = (
        ('UNCLASSIFIED', 'unclassified'),
        ('CONFIDENTIAL', 'confidential'),
        ('SECRET', 'secret'),
        ('TOPSECRET', 'top secret'),
    )

    status = models.CharField(
        max_length=32,
        choices=CLASS_STATUS,
        default='UNCLASSIFIED',)

    def __str__(self):
        return f'{self.status}'

class Sitename(models.Model):
    sitename = models.CharField(max_length=128)
    theme = models.CharField(max_length=128, null=True, blank=True, help_text="Set site theme.")
    def __str__(self):
        return f'{self.sitename}'


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

  @classmethod
  def enable_experimental_evidence(cls):
    return cls.objects.get(setting="enable_experimental_evidence").active
