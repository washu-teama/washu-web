# Generated by Django 2.1.2 on 2019-05-16 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinator',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
