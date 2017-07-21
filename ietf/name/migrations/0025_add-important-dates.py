# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-19 07:07
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('name', '0024_merge_20170606_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportantDateName',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('used', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('default_offset_days', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['order', 'name'],
                'abstract': False,
            },
        ),
    ]
