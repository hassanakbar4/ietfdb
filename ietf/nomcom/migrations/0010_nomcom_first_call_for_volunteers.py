# Generated by Django 2.2.20 on 2021-04-22 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nomcom', '0009_auto_20201109_0439'),
    ]

    operations = [
        migrations.AddField(
            model_name='nomcom',
            name='first_call_for_volunteers',
            field=models.DateField(blank=True, null=True, verbose_name='Date of the first call for volunteers'),
        ),
    ]
