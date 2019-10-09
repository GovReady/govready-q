# Generated by Django 2.0.13 on 2019-07-08 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0026_auto_20190515_1935'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='The title of this Portfolio.', max_length=256)),
                ('description', models.CharField(blank=True, help_text='A description of this Portfolio.', max_length=512)),
                ('projects', models.ManyToManyField(blank=True, help_text='The Projects that are listed within this Portfolio.', related_name='in_folders', to='siteapp.Project')),
            ],
            options={
                'permissions': ('can_grant_portfolio_owner_permission', 'Grant a user portfolio owner permission'),
            },
        ),
        migrations.AlterField(
            model_name='invitation',
            name='from_project',
            field=models.ForeignKey(blank=True, help_text='The Project within which the invitation exists.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to='siteapp.Project'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='from_portfolio',
            field=models.ForeignKey(blank=True, help_text='The Portfolio within which the invitation exists.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_invitations_sent', to='siteapp.Portfolio'),
        ),
    ]
