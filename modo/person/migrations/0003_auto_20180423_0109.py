# Generated by Django 2.0.4 on 2018-04-23 01:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0002_auto_20180421_0011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='human',
            name='identifier',
            field=models.BigIntegerField(default=6433506827972317, primary_key=True, serialize=False, unique=True, verbose_name='identifier'),
        ),
        migrations.AlterField(
            model_name='human',
            name='registered_since',
            field=models.DateField(default=datetime.date(2018, 4, 23), verbose_name='registerd since'),
        ),
    ]