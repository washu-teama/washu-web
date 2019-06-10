# Generated by Django 2.1.2 on 2019-05-17 14:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0009_auto_20190517_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinator',
            name='access_token',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='access_token_expired_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='hk_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='hk_pwd',
            field=models.CharField(default='', max_length=200),
        ),
    ]