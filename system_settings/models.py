from django.db import models
from django.core.exceptions import ValidationError

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
    def __str__(self):
        return f'{self.sitename}'


class SystemSettings(models.Model):
  """Model for various system settings for install of GovReady"""

  TYPE_CHOICES = (("0", ""), ("1", "Boolean"), ("2", "Number"), ("3", "Text"),)
  setting = models.CharField(max_length=200, unique=True)
  value = models.CharField(max_length=200, null=True, blank=True, help_text="")
  value_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=0)
  description = models.CharField(max_length=200, null=True, blank=True)
  active = models.BooleanField(default=False)

  def clean(self):
      type = self.value_type
      value = self.value
      if type == "0" and value:
          raise ValidationError("Value type is required if value is specified!")
      if not value and type != "0":
          raise ValidationError("Value is required if value type is specified!")
      if type == "1" and not isinstance(value, (bool)):
          raise ValidationError("Value type is specified as Boolean but value is not a Boolean!")
      if type == "2" and not value.isdigit():
          raise ValidationError("Value type is specified as Number but value is not a Number!")

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

  @classmethod
  def inactivity_timeout(cls):
      return cls.objects.get(setting="inactivity_timeout").active


