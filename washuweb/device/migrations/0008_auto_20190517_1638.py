# Generated by Django 2.1.2 on 2019-05-17 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0007_smartplugowner_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smartplugowner',
            name='status',
        ),
        migrations.AddField(
            model_name='smartplug',
            name='status',
            field=models.IntegerField(choices=[(0, 'disconnect'), (1, 'on'), (2, 'off')], default=0),
        ),
    ]
