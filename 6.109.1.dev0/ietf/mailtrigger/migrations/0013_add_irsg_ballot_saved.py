# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-04 13:12
from __future__ import unicode_literals

from django.db import migrations

def forward(apps, shema_editor):
    Recipient = apps.get_model('mailtrigger','Recipient')

    irsg = Recipient.objects.create(
        slug = 'irsg',
        desc = 'The IRSG',
        template = 'The IRSG <irsg@irtf.org>'
    )

    MailTrigger = apps.get_model('mailtrigger', 'MailTrigger')
    slug = 'irsg_ballot_saved'
    desc = 'Recipients when a new IRSG ballot position with comments is saved'
    irsg_ballot_saved = MailTrigger.objects.create(
        slug=slug,
        desc=desc
    )
    irsg_ballot_saved.to.add(irsg)
    cclist = []
    for ccstr in ['doc_affecteddoc_authors','doc_affecteddoc_group_chairs','doc_affecteddoc_notify','doc_authors','doc_group_chairs','doc_group_mail_list','doc_notify','doc_shepherd']:
        cclist.append(Recipient.objects.filter(slug=ccstr))
    irsg_ballot_saved.cc.set(cclist)

    MailTrigger.objects.filter(slug='ballot_saved').update(slug='iesg_ballot_saved')

def reverse(apps, shema_editor):
    MailTrigger = apps.get_model('mailtrigger', 'MailTrigger')
    MailTrigger.objects.filter(slug='irsg_ballot_saved').delete()
    MailTrigger.objects.filter(slug='iesg_ballot_saved').update(slug='ballot_saved')
    Recipient = apps.get_model('mailtrigger','Recipient')
    Recipient.objects.filter(slug='irsg').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('mailtrigger', '0012_dont_last_call_early_reviews'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
