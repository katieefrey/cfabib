# Generated by Django 3.0.4 on 2021-02-03 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibtool', '0020_newarticle_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newarticle',
            name='status',
        ),
    ]
