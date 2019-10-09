# Generated by Django 2.0.9 on 2019-04-03 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    atomic = False # required for migrations that rename tables in Sqlite

    dependencies = [
        ('guidedmodules', '0046_auto_20180528_1835'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AppInstance',
            new_name='AppVersion',
        ),
        migrations.AlterField(
            model_name='module',
            name='app',
            field=models.ForeignKey(help_text='The AppVersion that this Module is a part of. Null for legacy Modules created before we had this field.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='guidedmodules.AppVersion'),
        ),
        migrations.AlterField(
            model_name='module',
            name='module_name',
            field=models.SlugField(help_text='A slug-like identifier for the Module that is unique within the AppVersion app.', max_length=200),
        ),
        migrations.AlterField(
            model_name='appversion',
            name='source',
            field=models.ForeignKey(help_text='The source repository where this AppVersion came from.', on_delete=django.db.models.deletion.CASCADE, related_name='appversions', to='guidedmodules.AppSource'),
        ),
        migrations.AlterField(
            model_name='appversion',
            name='system_app',
            field=models.NullBooleanField(default=None, help_text='Set to True for AppVersions that are the current version of a system app that provides system-expected Modules. A constraint ensures that only one (source, name) pair can be true.'),
        ),
    ]
