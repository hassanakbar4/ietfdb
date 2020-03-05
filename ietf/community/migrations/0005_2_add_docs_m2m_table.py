# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-22 08:15


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0005_1_del_docs_m2m_table'),
    ]

    # The implementation of AlterField in Django 1.11 applies
    #   'ALTER TABLE <table> MODIFY <field> ...;' in order to fix foregn keys
    #   to the altered field, but as it seems does _not_ fix up m2m
    #   intermediary tables in an equivalent manner, so here we remove and
    #   then recreate the m2m tables so they will have the appropriate field
    #   types.

    operations = [
        # Add fields back (will create the m2m tables with the right field types)
        migrations.AddField(
            model_name='communitylist',
            name='added_docs',
            field=models.ManyToManyField(to='doc.Document'),
        ),
        migrations.AddField(
            model_name='searchrule',
            name='name_contains_index',
            field=models.ManyToManyField(to='doc.Document'),
        ),
    ]
