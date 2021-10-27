# Generated by Django 2.0.13 on 2020-08-07 09:30

from django.db import migrations
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0035_add_session_origin'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='base',
            field=ietf.utils.models.ForeignKey(blank=True, help_text='Sessions scheduled in the base show up in this schedule.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='derivedschedule_set', to='meeting.Schedule'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='origin',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='meeting.Schedule'),
        ),
    ]
