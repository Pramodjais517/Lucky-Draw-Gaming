# Generated by Django 3.0 on 2021-02-04 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20210204_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(max_length=100),
        ),
    ]
