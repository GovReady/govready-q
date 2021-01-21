# Generated by Django 3.0.11 on 2021-01-21 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guidedmodules', '0053_auto_20210121_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appversion',
            name='trust_inputs',
            field=models.BooleanField(default=False, help_text='Are inputs trusted? Inputs include OSCAL components and statements that will be served on our domain.', null=True),
        ),
    ]