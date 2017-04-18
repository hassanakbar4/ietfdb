# Copyright The IETF Trust 2016, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import socket

from django.core.management.base import BaseCommand

import debug                            # pyflakes:ignore

from ietf.nomcom.factories import nomcom_kwargs_for_year, NomComFactory, NomineePositionFactory, key
from ietf.person.factories import EmailFactory
from ietf.group.models import Group
from ietf.person.models import User

class Command(BaseCommand):
    help = (u"Create (or delete) a dummy nomcom for test and development purposes.")

    def add_arguments(self, parser):
        parser.add_argument('--delete', dest='delete', action='store_true', help='Delete the test and development dummy nomcom')

    def handle(self, *args, **options):
        if socket.gethostname().split('.')[0] in ['core3', 'ietfa', 'ietfb', 'ietfc', ]:
            raise EnvironmentError("Refusing to create a dummy nomcom on a production server")

        opt_delete = options.get('delete', False)
        if opt_delete:
            if Group.objects.filter(acronym='nomcom7437').exists():
                Group.objects.filter(acronym='nomcom7437').delete()
                User.objects.filter(username__in=['dummychair','dummymember','dummycandidate']).delete()
                self.stdout.write("Deleted dummy group 'nomcom7437' and its related objects.")
            else:
                self.stderr.write("Dummy nomcom 'nomcom7437' does not exist; nothing to do.\n")
        else:
            if Group.objects.filter(acronym='nomcom7437').exists():
                self.stderr.write("Dummy nomcom 'nomcom7437' already exists; nothing to do.\n")
            else:
                nc = NomComFactory.create(**nomcom_kwargs_for_year(year=7437,
                                                                  populate_personnel=False,
                                                                  populate_positions=False))

                e = EmailFactory(person__name=u'Dummy Chair',address=u'dummychair@example.com',person__user__username=u'dummychair',person__default_emails=False)
                e.person.user.set_password('password')
                e.person.user.save()
                nc.group.role_set.create(name_id=u'chair',person=e.person,email=e)

                e = EmailFactory(person__name=u'Dummy Member',address=u'dummymember@example.com',person__user__username=u'dummymember',person__default_emails=False)
                e.person.user.set_password('password')
                e.person.user.save()
                nc.group.role_set.create(name_id=u'member',person=e.person,email=e)


                e = EmailFactory(person__name=u'Dummy Candidate',address=u'dummycandidate@example.com',person__user__username=u'dummycandidate',person__default_emails=False)
                e.person.user.set_password('password')
                e.person.user.save()
                NomineePositionFactory(nominee__nomcom=nc, nominee__person=e.person,
                                       position__nomcom=nc, position__name=u'Dummy Area Director',
                                      )

                self.stdout.write("%s\n" % key)
                self.stdout.write("Nomcom 7437 created. The private key can also be found at any time\nin ietf/nomcom/factories.py. Note that it is NOT a secure key.\n")

