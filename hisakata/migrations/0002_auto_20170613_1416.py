# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 05:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hisakata', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='playing',
            old_name='player_1_or_2',
            new_name='player_num',
        ),
        migrations.AlterField(
            model_name='round',
            name='round',
            field=models.IntegerField(default=0),
        ),
    ]