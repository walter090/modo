# Generated by Django 2.0.4 on 2018-04-29 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='topic',
            field=models.CharField(default='general', max_length=20, verbose_name='category'),
        ),
    ]
