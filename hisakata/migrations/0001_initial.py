# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 03:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Date',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('winner', models.IntegerField(choices=[(0, 'Undecided'), (1, 'player1'), (2, 'player2')], default=0)),
                ('result', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Playing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_1_or_2', models.IntegerField(choices=[(1, 'player1'), (2, 'player2')], default=1)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hisakata.Match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hisakata.Player')),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.IntegerField(default=1)),
                ('class_date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hisakata.Date')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='match',
            field=models.ManyToManyField(through='hisakata.Playing', to='hisakata.Match'),
        ),
        migrations.AddField(
            model_name='match',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hisakata.Round'),
        ),
    ]
