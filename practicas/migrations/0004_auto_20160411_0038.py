# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-11 04:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('practicas', '0003_auto_20160410_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workplace',
            name='address',
            field=models.CharField(max_length=250, verbose_name='dirección'),
        ),
    ]