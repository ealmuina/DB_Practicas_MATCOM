# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-12 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('practicas', '0009_auto_20160412_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participation',
            name='grade',
            field=models.IntegerField(blank=True, verbose_name='calificación'),
        ),
    ]
