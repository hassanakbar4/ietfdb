# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from __future__ import absolute_import, print_function, unicode_literals

import six
if six.PY3:
    from typing import List, Tuple      # pyflakes:ignore

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]                                   # type: List[Tuple[str]]

    operations = [
        migrations.CreateModel(
            name='DBTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('variables', models.TextField(blank=True, null=True)),
                ('content', models.TextField()),
            ],
        ),
    ]
