# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-03 00:24


from django.db import migrations

def forward(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger', 'MailTrigger')
    Recipient = apps.get_model('mailtrigger', 'Recipient')

    changed = MailTrigger.objects.create(
        slug = 'ballot_ednote_changed_late',
        desc = 'Recipients when the RFC Editor note for a document is changed after the document has been approved',
    )
    changed.to.set(Recipient.objects.filter(slug__in=['rfc_editor','iesg']))

def reverse(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger','MailTrigger')
    MailTrigger.objects.filter(slug='ballot_ednote_changed_late').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('mailtrigger', '0003_add_review_notify_ad'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
