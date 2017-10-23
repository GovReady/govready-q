# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

# For any Module with an AppInstance, chop of the ModuleSource.namespace
# and AppInstance.appname from the Module key.
def forwards_func(apps, schema_editor):
    Module = apps.get_model("guidedmodules", "Module")
    db_alias = schema_editor.connection.alias
    for m in Module.objects.using(db_alias).exclude(app=None)\
        .select_related("source", "app"):
        if m.module_name.startswith(m.source.namespace+"/"+m.app.appname+"/"):
            m.module_name = m.module_name[len(m.source.namespace)+1+len(m.app.appname)+1:]
        m.save(using=db_alias)

# For any Module with an AppInstance, add the ModuleSource.namespace
# and AppInstance.appname to the Module key.
def reverse_func(apps, schema_editor):
    Module = apps.get_model("guidedmodules", "Module")
    db_alias = schema_editor.connection.alias
    Module.objects.using(db_alias)
    for m in Module.objects.using(db_alias).exclude(app=None)\
        .select_related("source", "app"):
        m.module_name = m.source.namespace + "/" + m.app.appname + "/" + m.module_name
        m.save(using=db_alias)

class Migration(migrations.Migration):

    dependencies = [
        ('guidedmodules', '0029_auto_20170920_1443'),
    ]

    operations = [
        migrations.RenameField(
            model_name='module',
            old_name='key',
            new_name='module_name',
        ),
        migrations.AlterField(
            model_name='module',
            name='module_name',
            field=models.SlugField(help_text='A slug-like identifier for the Module that is unique within the AppInstance app.', max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='module',
            unique_together=set([('app', 'module_name')]),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
