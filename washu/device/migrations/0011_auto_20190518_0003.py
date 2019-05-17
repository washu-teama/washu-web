# Generated by Django 2.1.2 on 2019-05-17 15:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('device', '0010_auto_20190517_2308'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartPlugEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('event', models.IntegerField(choices=[(0, 'enter'), (1, 'leave')])),
                ('do', models.IntegerField(choices=[(0, 'off'), (1, 'on')])),
            ],
        ),
        migrations.AlterField(
            model_name='smartplug',
            name='status',
            field=models.IntegerField(choices=[(0, 'off'), (1, 'on'), (2, 'disconnect')], default=2),
        ),
        migrations.AddField(
            model_name='smartplugevent',
            name='smartplug',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='device.SmartPlug'),
        ),
        migrations.AddField(
            model_name='smartplugevent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
