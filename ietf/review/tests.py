# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-


from __future__ import absolute_import, print_function, unicode_literals

from ietf.review.factories import ReviewAssignmentFactory, ReviewRequestFactory
from ietf.utils.test_utils import TestCase, reload_db_objects
from .mailarch import hash_list_message_id

class HashTest(TestCase):

    def test_hash_list_message_id(self):
        for list, msgid, hash in (
                ('ietf', '156182196167.12901.11966487185176024571@ietfa.amsl.com',  b'lr6RtZ4TiVMZn1fZbykhkXeKhEk'),
                ('codesprints', 'E1hNffl-0004RM-Dh@zinfandel.tools.ietf.org',       b'N1nFHHUXiFWYtdzBgjtqzzILFHI'),
                ('xml2rfc', '3A0F4CD6-451F-44E2-9DA4-28235C638588@rfc-editor.org',  b'g6DN4SxJGDrlSuKsubwb6rRSePU'),
                (u'ietf', u'156182196167.12901.11966487185176024571@ietfa.amsl.com',b'lr6RtZ4TiVMZn1fZbykhkXeKhEk'),
                (u'codesprints', u'E1hNffl-0004RM-Dh@zinfandel.tools.ietf.org',     b'N1nFHHUXiFWYtdzBgjtqzzILFHI'),
                (u'xml2rfc', u'3A0F4CD6-451F-44E2-9DA4-28235C638588@rfc-editor.org',b'g6DN4SxJGDrlSuKsubwb6rRSePU'),
                (b'ietf', b'156182196167.12901.11966487185176024571@ietfa.amsl.com',b'lr6RtZ4TiVMZn1fZbykhkXeKhEk'),
                (b'codesprints', b'E1hNffl-0004RM-Dh@zinfandel.tools.ietf.org',     b'N1nFHHUXiFWYtdzBgjtqzzILFHI'),
                (b'xml2rfc', b'3A0F4CD6-451F-44E2-9DA4-28235C638588@rfc-editor.org',b'g6DN4SxJGDrlSuKsubwb6rRSePU'),
            ):
            self.assertEqual(hash, hash_list_message_id(list, msgid))
            

class ReviewAssignmentTest(TestCase):
    def test_update_review_req_status(self):
        review_req = ReviewRequestFactory(state_id='assigned')
        ReviewAssignmentFactory(review_request=review_req, state_id='part-completed')
        assignment = ReviewAssignmentFactory(review_request=review_req)

        assignment.state_id = 'no-response'
        assignment.save()
        review_req = reload_db_objects(review_req)
        self.assertEqual(review_req.state_id, 'requested')

    def test_no_update_review_req_status_when_other_active_assignment(self):
        # If there is another still active assignment, do not update review_req state
        review_req = ReviewRequestFactory(state_id='assigned')
        ReviewAssignmentFactory(review_request=review_req, state_id='assigned')
        assignment = ReviewAssignmentFactory(review_request=review_req)

        assignment.state_id = 'no-response'
        assignment.save()
        review_req = reload_db_objects(review_req)
        self.assertEqual(review_req.state_id, 'assigned')

    def test_no_update_review_req_status_when_review_req_withdrawn(self):
        # review_req state must only be changed to "requested", if old state was "assigned",
        # to prevent reviving dead review requests
        review_req = ReviewRequestFactory(state_id='withdrawn')
        assignment = ReviewAssignmentFactory(review_request=review_req)

        assignment.state_id = 'no-response'
        assignment.save()
        review_req = reload_db_objects(review_req)
        self.assertEqual(review_req.state_id, 'withdrawn')
