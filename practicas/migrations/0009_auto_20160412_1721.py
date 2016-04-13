# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-12 21:21
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('practicas', '0008_auto_20160412_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requirement',
            name='year',
            field=models.IntegerField(validators=[
                django.core.validators.MinValueValidator(1, message='Toda carrera tiene duración mayor que 1 año.')],
                                      verbose_name='año'),
        ),
    ]
