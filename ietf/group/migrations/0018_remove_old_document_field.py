# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-25 06:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0017_remove_docs2_m2m'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='charter',
        ),
    ]
