# Generated by Django 3.2.16 on 2022-10-31 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0084_auto_20221025_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='Revisions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True, null=True)),
                ('title', models.CharField(help_text='A name given to the document revision, which may be used by a tool for display and navigation.', max_length=250)),
                ('published', models.DateTimeField(blank=True, help_text='The date and time the document was published.', null=True)),
                ('last_modified', models.DateTimeField(blank=True, help_text='The date and time the document was last modified.', null=True)),
                ('version', models.CharField(default='1.0', help_text='A string used to distinguish the current version of the document from other previous (and future) versions.', max_length=20)),
                ('oscal_version', models.CharField(blank=True, default='1.0.0', help_text='OSCAL version number.', max_length=20, null=True)),
                ('remarks', models.TextField(help_text='Additional commentary on the containing object.')),
                ('links', models.ManyToManyField(blank=True, related_name='revisions', to='controls.Link')),
                ('props', models.ManyToManyField(blank=True, related_name='revisions', to='controls.Prop')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]