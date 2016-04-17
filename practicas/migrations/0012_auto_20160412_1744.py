# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-12 21:44
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('practicas', '0011_auto_20160412_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participation',
            name='grade',
            field=models.PositiveIntegerField(blank=True, validators=[
                django.core.validators.MaxValueValidator(5, 'La máxima calificación es 5.')],
                                              verbose_name='calificación'),
        ),
        migrations.AlterField(
            model_name='requirement',
            name='students_count',
            field=models.IntegerField(validators=django.core.validators.MinValueValidator(1,
                                                                                          'En el proyecto debe participar al menos 1 estudiante.'),
                                      verbose_name='cantidad de estudiantes'),
        ),
        migrations.AlterField(
            model_name='workplace',
            name='phone',
            field=models.PositiveIntegerField(verbose_name='teléfono'),
        ),
    ]