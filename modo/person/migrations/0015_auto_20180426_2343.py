# Generated by Django 2.0.4 on 2018-04-26 23:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0014_auto_20180426_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='human',
            name='registered_since',
            field=models.DateField(default=datetime.date.today, verbose_name='registerd since'),
        ),
    ]
