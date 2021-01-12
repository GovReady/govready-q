# Generated by Django 3.0.7 on 2020-12-24 15:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0033_auto_20201129_1913'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Unique identifier for this Import Record.')),
            ],
        ),
        migrations.AddField(
            model_name='element',
            name='import_record',
            field=models.ForeignKey(blank=True, help_text='The Import Record which created this Element.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='import_record_elements', to='controls.ImportRecord'),
        ),
        migrations.AddField(
            model_name='statement',
            name='import_record',
            field=models.ForeignKey(blank=True, help_text='The Import Record which created this Statement.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='import_record_statements', to='controls.ImportRecord'),
        ),
    ]
