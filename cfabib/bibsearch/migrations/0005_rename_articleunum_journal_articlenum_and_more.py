# Generated by Django 5.0.4 on 2024-04-26 23:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bibsearch", "0004_rename_articlenum_journal_articleunum_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="journal",
            old_name="articleunum",
            new_name="articlenum",
        ),
        migrations.RemoveField(
            model_name="journal",
            name="articlevnum",
        ),
    ]