# Generated by Django 3.0.4 on 2021-01-25 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bibtool', '0014_auto_20210125_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='status',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='bibtool.Status'),
            preserve_default=False,
        ),
    ]