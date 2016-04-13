# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-13 06:04
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('practicas', '0015_auto_20160413_0115'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredstudent',
            name='year',
            field=models.IntegerField(default=1, validators=[
                django.core.validators.MinValueValidator(1, message='Las carreras comienzan a partir del año 1.')],
                                      verbose_name='año'),
            preserve_default=False,
        ),
    ]
