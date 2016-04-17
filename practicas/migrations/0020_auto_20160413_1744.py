# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-13 21:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('practicas', '0019_auto_20160413_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='end',
            field=models.DateField(unique=True, verbose_name='Fecha de finalización'),
        ),
        migrations.AlterField(
            model_name='course',
            name='practice_end',
            field=models.DateField(unique=True, verbose_name='fecha de finalización de las prácticas'),
        ),
        migrations.AlterField(
            model_name='course',
            name='practice_start',
            field=models.DateField(unique=True, verbose_name='fecha de inicio de las prácticas'),
        ),
        migrations.AlterField(
            model_name='course',
            name='start',
            field=models.DateField(unique=True, verbose_name='fecha de inicio'),
        ),
        migrations.AlterField(
            model_name='major',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='workplace',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='nombre'),
        ),
        migrations.AlterUniqueTogether(
            name='registeredstudent',
            unique_together=set([('student', 'course')]),
        ),
        migrations.AlterUniqueTogether(
            name='requirement',
            unique_together=set([('project', 'major', 'year')]),
        ),
    ]