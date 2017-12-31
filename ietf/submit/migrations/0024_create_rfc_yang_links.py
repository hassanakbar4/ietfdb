# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-01 14:00
from __future__ import unicode_literals, print_function

import os
import json
from tqdm import tqdm

from django.db import migrations
from django.conf import settings

import debug                            # pyflakes:ignore

from ietf.submit.checkers import DraftYangChecker

def get_file_name(draft):
    return os.path.join(settings.INTERNET_ALL_DRAFTS_ARCHIVE_DIR, '%s-%s.txt'%(draft.name, draft.rev))

YANG_RFCS = [ 5717, 6021, 6022, 6087, 6095, 6241, 6243, 6470, 6536, 6643,
    6728, 6991, 7223, 7224, 7277, 7317, 7407, 7758, 7895, 7952, 8022, 8040,
    8049, 8072, 8177, 8194, 8294, ]

def forwards(apps, schema_editor):
    DocAlias = apps.get_model('doc', 'DocAlias')
    SubmissionCheck = apps.get_model('submit', 'SubmissionCheck')
    checker = DraftYangChecker()

    for rfc_number in tqdm(YANG_RFCS):
        draft = DocAlias.objects.get(name="rfc%s" % rfc_number).document
        submission = draft.submission_set.filter(rev=draft.rev).order_by('-id').first()
        if submission:
                result = checker.check_file_txt(get_file_name(draft))
                passed, message, errors, warnings, items = result
                items = json.loads(json.dumps(items))
                items['draft'] = draft.name
                items['rev'] = draft.rev
                check = SubmissionCheck.objects.create(submission=submission, checker=checker.name, passed=passed,
                                                message=message, errors=errors, warnings=warnings, items=items,
                                                symbol=checker.symbol)
                if 'code' in check.items and check.items['code']:
                    code = check.items['code']
                    if 'yang' in code:
                        modules = code['yang']
                        # Yang impact analysis URL
                        draft.documenturl_set.filter(tag_id='yang-impact-analysis').delete()
                        f = settings.SUBMIT_YANG_CATALOG_MODULEARG
                        moduleargs = '&'.join([ f.format(module=m) for m in modules])
                        url  = settings.SUBMIT_YANG_CATALOG_IMPACT_URL.format(moduleargs=moduleargs, draft=draft.name)
                        desc = settings.SUBMIT_YANG_CATALOG_IMPACT_DESC.format(modules=','.join(modules), draft=draft.name)
                        draft.documenturl_set.create(url=url[:512], tag_id='yang-impact-analysis', desc=desc)
                        # Yang module metadata URLs
                        old_urls = draft.documenturl_set.filter(tag_id='yang-module-metadata')
                        old_urls.delete()
                        for module in modules:
                            url  = settings.SUBMIT_YANG_CATALOG_MODULE_URL.format(module=module)
                            desc = settings.SUBMIT_YANG_CATALOG_MODULE_DESC.format(module=module)
                            draft.documenturl_set.create(url=url[:512], tag_id='yang-module-metadata', desc=desc)

def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0023_create_draft_yang_links'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
