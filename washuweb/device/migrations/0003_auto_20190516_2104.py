# Generated by Django 2.1.2 on 2019-05-16 12:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0002_coordinator_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordinator',
            name='active',
        ),
        migrations.AddField(
            model_name='coordinator',
            name='last_signal',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
