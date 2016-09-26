# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-26 07:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_student_allowed_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='courserecommendation',
            name='school',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='portal.School'),
            preserve_default=False,
        ),
    ]
