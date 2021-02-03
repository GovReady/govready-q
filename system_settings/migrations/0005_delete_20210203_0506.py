# Created by Greg Elin on 2021-02-03 05:06

from django.db import migrations


def del_experimental_oscal(apps, schema_editor):
    SystemSettings = apps.get_model('system_settings', 'SystemSettings')
    enable_experimental_oscal = SystemSettings.objects.filter(setting='enable_experimental_oscal').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('system_settings', '0003_auto_20200623_1539'),
        ('system_settings', '0004_merge_20200623_1550'),
    ]

    operations = [
        migrations.RunPython(del_experimental_oscal),
    ]
