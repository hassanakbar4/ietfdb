# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-30 08:17


from django.db import migrations

def forward(apps, schema_editor):
    ReviewAssignmentDocEvent = apps.get_model('doc','ReviewAssignmentDocEvent')
    for event in ReviewAssignmentDocEvent.objects.filter(type="closed_review_assignment",state_id='rejected',review_assignment__completed_on__isnull=True):
        event.review_assignment.completed_on = event.time
        event.review_assignment.save()


def reverse(apps, schema_editor):
    # There's no harm in leaving the newly set completed_on values even if this is rolled back
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0014_document_primary_key_cleanup'),
        ('doc', '0026_add_draft_rfceditor_state'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
