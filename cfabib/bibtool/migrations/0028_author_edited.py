# Generated by Django 3.0.4 on 2021-02-11 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bibtool', '0027_auto_20210205_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='edited',
            field=models.BooleanField(default=False),
        ),
    ]
