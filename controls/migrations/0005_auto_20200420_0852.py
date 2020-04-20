# Generated by Django 2.2.12 on 2020-04-20 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0004_auto_20200417_1615'),
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Common name or acronym of the element', max_length=250)),
                ('full_name', models.CharField(blank=True, help_text='Full name of the element', max_length=250, null=True)),
                ('description', models.CharField(help_text='Brief description of the CommonControlProvider', max_length=255)),
                ('element_type', models.CharField(blank=True, help_text='Statement type', max_length=150, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.AlterField(
            model_name='commoncontrol',
            name='name',
            field=models.CharField(blank=True, help_text='Name of the CommonControl', max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='commoncontrolprovider',
            name='name',
            field=models.CharField(help_text='Name of the CommonControlProvider', max_length=150),
        ),
        migrations.CreateModel(
            name='Statement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sid', models.CharField(help_text='Statement identifier such as OSCAL formatted Control ID', max_length=100)),
                ('sid_class', models.CharField(help_text="Statement identifier 'class' such as '800-53rev4' or other OSCAL catalog name Control ID ", max_length=200)),
                ('body', models.TextField(blank=True, help_text='The statement itself', null=True)),
                ('statement_type', models.CharField(blank=True, help_text='Statement type', max_length=150, null=True)),
                ('remarks', models.TextField(blank=True, help_text='The statement itself', null=True)),
                ('version', models.CharField(blank=True, help_text='Optional version number', max_length=20, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('parent', models.ForeignKey(blank=True, help_text='Optional version number', null=True, on_delete=django.db.models.deletion.SET_NULL, to='controls.Statement')),
            ],
        ),
    ]
