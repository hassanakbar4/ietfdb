import json

from pyquery import PyQuery

from django.core.urlresolvers import reverse as urlreverse
from django.contrib.auth.models import User

from ietf.community.models import CommunityList, SearchRule, EmailSubscription
from ietf.community.utils import docs_matching_community_list_rule, community_list_rules_matching_doc
from ietf.doc.models import State
from ietf.doc.utils import add_state_change_event
from ietf.person.models import Person
from ietf.utils.test_data import make_test_data
from ietf.utils.test_utils import login_testing_unauthorized, TestCase
from ietf.utils.mail import outbox

class CommunityListTests(TestCase):
    def test_rule_matching(self):
        draft = make_test_data()
        iesg_state = State.objects.get(type="draft-iesg", slug="lc")
        draft.set_state(iesg_state)

        clist = CommunityList.objects.create(user=User.objects.get(username="plain"))

        rule_group = SearchRule.objects.create(rule_type="group", group=draft.group, state=State.objects.get(type="draft", slug="active"), community_list=clist)
        rule_group_rfc = SearchRule.objects.create(rule_type="group_rfc", group=draft.group, state=State.objects.get(type="draft", slug="rfc"), community_list=clist)
        rule_area = SearchRule.objects.create(rule_type="area", group=draft.group.parent, state=State.objects.get(type="draft", slug="active"), community_list=clist)

        rule_state_iesg = SearchRule.objects.create(rule_type="state_iesg", state=State.objects.get(type="draft-iesg", slug="lc"), community_list=clist)

        rule_author = SearchRule.objects.create(rule_type="author", state=State.objects.get(type="draft", slug="active"), person=Person.objects.filter(email__documentauthor__document=draft).first(), community_list=clist)

        rule_ad = SearchRule.objects.create(rule_type="ad", state=State.objects.get(type="draft", slug="active"), person=draft.ad, community_list=clist)

        rule_shepherd = SearchRule.objects.create(rule_type="shepherd", state=State.objects.get(type="draft", slug="active"), person=draft.shepherd.person, community_list=clist)

        rule_name_contains = SearchRule.objects.create(rule_type="name_contains", state=State.objects.get(type="draft", slug="active"), text="-".join(draft.name.split("-")[2:]), community_list=clist)

        # doc -> rules
        matching_rules = list(community_list_rules_matching_doc(draft))
        self.assertTrue(rule_group in matching_rules)
        self.assertTrue(rule_group_rfc not in matching_rules)
        self.assertTrue(rule_area in matching_rules)
        self.assertTrue(rule_state_iesg in matching_rules)
        self.assertTrue(rule_author in matching_rules)
        self.assertTrue(rule_ad in matching_rules)
        self.assertTrue(rule_shepherd in matching_rules)
        self.assertTrue(rule_name_contains in matching_rules)

        # rule -> docs
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_group)))
        self.assertTrue(draft not in list(docs_matching_community_list_rule(rule_group_rfc)))
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_area)))
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_state_iesg)))
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_author)))
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_ad)))
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_shepherd)))
        self.assertTrue(draft in list(docs_matching_community_list_rule(rule_name_contains)))

    def test_view_list(self):
        draft = make_test_data()

        url = urlreverse("community_personal_view_list", kwargs={ "username": "plain" })

        # without list
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # with list
        clist = CommunityList.objects.create(user=User.objects.get(username="plain"))
        clist.added_docs.add(draft)
        SearchRule.objects.create(
            community_list=clist,
            rule_type="name_contains",
            state=State.objects.get(type="draft", slug="active"),
            text="test",
        )
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(draft.name in r.content)

    def test_manage_list(self):
        draft = make_test_data()

        url = urlreverse("community_personal_manage_list", kwargs={ "username": "plain" })
        login_testing_unauthorized(self, "plain", url)

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # add document
        r = self.client.post(url, { "action": "add_documents", "documents": draft.pk })
        self.assertEqual(r.status_code, 302)
        clist = CommunityList.objects.get(user__username="plain")
        self.assertTrue(clist.added_docs.filter(pk=draft.pk))

        # add rule
        r = self.client.post(url, {
            "action": "add_rule",
            "rule_type": "author_rfc",
            "author_rfc-person": Person.objects.filter(email__documentauthor__document=draft).first().pk,
            "author_rfc-state": State.objects.get(type="draft", slug="rfc").pk,
        })
        self.assertEqual(r.status_code, 302)
        clist = CommunityList.objects.get(user__username="plain")
        self.assertTrue(clist.searchrule_set.filter(rule_type="author_rfc"))

        # rule shows up on GET
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        rule = clist.searchrule_set.filter(rule_type="author_rfc").first()
        q = PyQuery(r.content)
        self.assertEqual(len(q('#r%s' % rule.pk)), 1)

        # remove rule
        r = self.client.post(url, {
            "action": "remove_rule",
            "rule": rule.pk,
        })

        clist = CommunityList.objects.get(user__username="plain")
        self.assertTrue(not clist.searchrule_set.filter(rule_type="author_rfc"))

    def test_track_untrack_document_for_personal_list_through_ajax(self):
        draft = make_test_data()

        url = urlreverse("community_personal_track_document", kwargs={ "username": "plain", "name": draft.name })
        login_testing_unauthorized(self, "plain", url)

        # track
        r = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.content)["success"], True)
        clist = CommunityList.objects.get(user__username="plain")
        self.assertEqual(list(clist.added_docs.all()), [draft])

        # untrack
        url = urlreverse("community_personal_untrack_document", kwargs={ "username": "plain", "name": draft.name })
        r = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.content)["success"], True)
        clist = CommunityList.objects.get(user__username="plain")
        self.assertEqual(list(clist.added_docs.all()), [])

    def test_track_untrack_document_for_group_list(self):
        draft = make_test_data()

        url = urlreverse("community_group_track_document", kwargs={ "acronym": draft.group.acronym, "name": draft.name })
        login_testing_unauthorized(self, "marschairman", url)

        # track
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        r = self.client.post(url)
        self.assertEqual(r.status_code, 302)
        clist = CommunityList.objects.get(group__acronym=draft.group.acronym)
        self.assertEqual(list(clist.added_docs.all()), [draft])

        # untrack
        url = urlreverse("community_group_untrack_document", kwargs={ "acronym": draft.group.acronym, "name": draft.name })
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        r = self.client.post(url)
        self.assertEqual(r.status_code, 302)
        clist = CommunityList.objects.get(group__acronym=draft.group.acronym)
        self.assertEqual(list(clist.added_docs.all()), [])

    def test_csv(self):
        draft = make_test_data()

        url = urlreverse("community_personal_csv", kwargs={ "username": "plain" })

        # without list
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # with list
        clist = CommunityList.objects.create(user=User.objects.get(username="plain"))
        clist.added_docs.add(draft)
        SearchRule.objects.create(
            community_list=clist,
            rule_type="name_contains",
            state=State.objects.get(type="draft", slug="active"),
            text="test",
        )
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        # this is a simple-minded test, we don't actually check the fields
        self.assertTrue(draft.name in r.content)

    def test_feed(self):
        draft = make_test_data()

        url = urlreverse("community_personal_feed", kwargs={ "username": "plain" })

        # without list
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # with list
        clist = CommunityList.objects.create(user=User.objects.get(username="plain"))
        clist.added_docs.add(draft)
        SearchRule.objects.create(
            community_list=clist,
            rule_type="name_contains",
            state=State.objects.get(type="draft", slug="active"),
            text="test",
        )
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(draft.name in r.content)

        # only significant
        r = self.client.get(url + "?significant=1")
        self.assertEqual(r.status_code, 200)
        self.assertTrue('<entry>' not in r.content)

    def extract_confirm_url(self, confirm_email):
        # dig out confirm_email link
        msg = confirm_email.get_payload(decode=True)
        line_start = "http"
        confirm_url = None
        for line in msg.split("\n"):
            if line.strip().startswith(line_start):
                confirm_url = line.strip()
        self.assertTrue(confirm_url)

        return confirm_url

    def test_subscription(self):
        draft = make_test_data()

        url = urlreverse("community_personal_subscription", kwargs={ "operation": "subscribe", "username": "plain" })

        # subscribe without list
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)

        # subscribe with list
        clist = CommunityList.objects.create(user=User.objects.get(username="plain"))
        clist.added_docs.add(draft)
        SearchRule.objects.create(
            community_list=clist,
            rule_type="name_contains",
            state=State.objects.get(type="draft", slug="active"),
            text="test",
        )
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # do subscribe
        mailbox_before = len(outbox)
        r = self.client.post(url, { "email": "subscriber@example.com", "notify_on": "significant" })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(outbox), mailbox_before + 1)

        # go to confirm page
        confirm_url = self.extract_confirm_url(outbox[-1])
        r = self.client.get(confirm_url)
        self.assertEqual(r.status_code, 200)

        # confirm subscribe
        r = self.client.post(confirm_url, { 'action': 'confirm' })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(EmailSubscription.objects.filter(community_list=clist, email="subscriber@example.com", significant=True).count(), 1)

        # unsubscribe
        url = urlreverse("community_personal_subscription", kwargs={ "operation": "unsubscribe", "username": "plain" })
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # do unsubscribe
        mailbox_before = len(outbox)
        r = self.client.post(url, { "email": "subscriber@example.com", "notify_on": "significant" })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(outbox), mailbox_before + 1)

        # go to confirm page
        confirm_url = self.extract_confirm_url(outbox[-1])
        r = self.client.get(confirm_url)
        self.assertEqual(r.status_code, 200)

        # confirm unsubscribe
        r = self.client.post(confirm_url, { 'action': 'confirm' })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(EmailSubscription.objects.filter(community_list=clist, email="subscriber@example.com", significant=True).count(), 0)

    def test_notification(self):
        draft = make_test_data()

        clist = CommunityList.objects.create(user=User.objects.get(username="plain"))
        clist.added_docs.add(draft)
        SearchRule.objects.create(
            community_list=clist,
            rule_type="name_contains",
            state=State.objects.get(type="draft", slug="active"),
            text="test",
        )

        EmailSubscription.objects.create(community_list=clist, email="subscriber@example.com", significant=True)

        mailbox_before = len(outbox)
        active_state = State.objects.get(type="draft", slug="active")
        system = Person.objects.get(name="(System)")
        add_state_change_event(draft, system, None, active_state)
        self.assertEqual(len(outbox), mailbox_before)

        mailbox_before = len(outbox)
        rfc_state = State.objects.get(type="draft", slug="rfc")
        add_state_change_event(draft, system, active_state, rfc_state)
        self.assertEqual(len(outbox), mailbox_before + 1)
        self.assertTrue(draft.name in outbox[-1]["Subject"])
        
        
