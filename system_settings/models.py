from django.db import models


class Classification(models.Model):
    CLASS_STATUS = (
        ('FOUO', 'fouo'),
        ('CONFIDENTIAL', 'confidential'),
        ('SECRET', 'secret'),
        ('TOPSECRET', 'top secret'),
    )

    status = models.CharField(
        max_length=16,
        choices=CLASS_STATUS,
        default='FOUO',)

    def __str__(self):
        #return get_status_display()
        return f'{self.status}'



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
