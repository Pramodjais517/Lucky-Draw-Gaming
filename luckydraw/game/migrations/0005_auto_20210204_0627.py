# Generated by Django 3.0 on 2021-02-04 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20210204_0539'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='ticket_number',
            new_name='code',
        ),
    ]
