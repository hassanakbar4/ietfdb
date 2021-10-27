# Copyright The IETF Trust 2018-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('review', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('name', '0001_initial'),
        ('submit', '0001_initial'),
        ('person', '0001_initial'),
        ('message', '0001_initial'),
        ('doc', '0001_initial'),
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='group',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group'),
        ),
        migrations.AddField(
            model_name='document',
            name='intended_std_level',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.IntendedStdLevelName', verbose_name='Intended standardization level'),
        ),
        migrations.AddField(
            model_name='document',
            name='shepherd',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shepherd_document_set', to='person.Email'),
        ),
        migrations.AddField(
            model_name='document',
            name='states',
            field=models.ManyToManyField(blank=True, to='doc.State'),
        ),
        migrations.AddField(
            model_name='document',
            name='std_level',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.StdLevelName', verbose_name='Standardization level'),
        ),
        migrations.AddField(
            model_name='document',
            name='stream',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.StreamName'),
        ),
        migrations.AddField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(blank=True, to='name.DocTagName'),
        ),
        migrations.AddField(
            model_name='document',
            name='type',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.DocTypeName'),
        ),
        migrations.AddField(
            model_name='docreminder',
            name='event',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.DocEvent'),
        ),
        migrations.AddField(
            model_name='docreminder',
            name='type',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.DocReminderTypeName'),
        ),
        migrations.AddField(
            model_name='dochistoryauthor',
            name='document',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentauthor_set', to='doc.DocHistory'),
        ),
        migrations.AddField(
            model_name='dochistoryauthor',
            name='email',
            field=ietf.utils.models.ForeignKey(blank=True, help_text='Email address used by author for submission', null=True, on_delete=django.db.models.deletion.CASCADE, to='person.Email'),
        ),
        migrations.AddField(
            model_name='dochistoryauthor',
            name='person',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='ad',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_dochistory_set', to='person.Person', verbose_name='area director'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_set', to='doc.Document'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='formal_languages',
            field=models.ManyToManyField(blank=True, help_text='Formal languages used in document', to='name.FormalLanguageName'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='group',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='intended_std_level',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.IntendedStdLevelName', verbose_name='Intended standardization level'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='shepherd',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shepherd_dochistory_set', to='person.Email'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='states',
            field=models.ManyToManyField(blank=True, to='doc.State'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='std_level',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.StdLevelName', verbose_name='Standardization level'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='stream',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.StreamName'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='tags',
            field=models.ManyToManyField(blank=True, to='name.DocTagName'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='type',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.DocTypeName'),
        ),
        migrations.AddField(
            model_name='docevent',
            name='by',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person'),
        ),
        migrations.AddField(
            model_name='docevent',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
        migrations.AddField(
            model_name='docalias',
            name='document',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
        migrations.AddField(
            model_name='deletedevent',
            name='by',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person'),
        ),
        migrations.AddField(
            model_name='deletedevent',
            name='content_type',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='ballottype',
            name='doc_type',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.DocTypeName'),
        ),
        migrations.AddField(
            model_name='ballottype',
            name='positions',
            field=models.ManyToManyField(blank=True, to='name.BallotPositionName'),
        ),
        migrations.AddField(
            model_name='submissiondocevent',
            name='submission',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submit.Submission'),
        ),
        migrations.AddField(
            model_name='statedocevent',
            name='state',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.State'),
        ),
        migrations.AddField(
            model_name='statedocevent',
            name='state_type',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.StateType'),
        ),
        migrations.AddField(
            model_name='reviewrequestdocevent',
            name='review_request',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='review.ReviewRequest'),
        ),
        migrations.AddField(
            model_name='reviewrequestdocevent',
            name='state',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='name.ReviewRequestStateName'),
        ),
        migrations.AddField(
            model_name='ballotpositiondocevent',
            name='ad',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person'),
        ),
        migrations.AddField(
            model_name='ballotpositiondocevent',
            name='ballot',
            field=ietf.utils.models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.BallotDocEvent'),
        ),
        migrations.AddField(
            model_name='ballotpositiondocevent',
            name='pos',
            field=ietf.utils.models.ForeignKey(default='norecord', on_delete=django.db.models.deletion.CASCADE, to='name.BallotPositionName', verbose_name='position'),
        ),
        migrations.AddField(
            model_name='ballotdocevent',
            name='ballot_type',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.BallotType'),
        ),
        migrations.AddField(
            model_name='addedmessageevent',
            name='in_reply_to',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doc_irtomanual', to='message.Message'),
        ),
        migrations.AddField(
            model_name='addedmessageevent',
            name='message',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doc_manualevents', to='message.Message'),
        ),
    ]
