# WG milestone editing views

import re, os, string, datetime, shutil

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson
from django.utils.html import mark_safe, escape
from django.utils.functional import lazy
from django.core.urlresolvers import reverse as urlreverse

from ietf.ietfauth.decorators import role_required, has_role
from ietf.doc.models import Document, DocEvent
from ietf.doc.utils import get_chartering_type
from ietf.group.models import *
from ietf.group.utils import save_group_in_history, save_milestone_in_history

def json_doc_names(docs):
    return simplejson.dumps([{"id": doc.pk, "name": doc.name } for doc in docs])

def parse_doc_names(s):
    return Document.objects.filter(pk__in=[x.strip() for x in s.split(",") if x.strip()], type="draft")

class MilestoneForm(forms.Form):
    id = forms.IntegerField(required=True, widget=forms.HiddenInput)

    desc = forms.CharField(max_length=500, label="Milestone", required=True)
    due = forms.DateField(required=True, label="Due date")
    resolved_checkbox = forms.BooleanField(required=False, label="Resolved")
    resolved = forms.CharField(max_length=50, required=False)

    delete = forms.BooleanField(required=False, initial=False)

    docs = forms.CharField(max_length=10000, required=False)

    accept = forms.BooleanField(required=False, initial=False)

    expanded_for_editing = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        m = self.milestone = kwargs.pop("instance", None)

        self.needs_review = kwargs.pop("needs_review", False)

        if m:
            if not "initial" in kwargs:
                kwargs["initial"] = {}
            kwargs["initial"].update(dict(id=m.pk,
                                          desc=m.desc,
                                          due=m.due,
                                          resolved_checkbox=bool(m.resolved),
                                          resolved=m.resolved,
                                          docs=",".join(m.docs.values_list("pk", flat=True)),
                                          ))

            kwargs["prefix"] = "m%s" % m.pk

            self.needs_review = m.state_id == "review"

        super(MilestoneForm, self).__init__(*args, **kwargs)

        pre = ""
        if not self.is_bound:
            pre = self.initial.get("docs", "")
        else:
            pre = self["docs"].data or ""

        self.fields["docs"].prepopulate = json_doc_names(parse_doc_names(pre))

    def clean_docs(self):
        s = self.cleaned_data["docs"]
        return Document.objects.filter(pk__in=[x.strip() for x in s.split(",") if x.strip()], type="draft")

    def clean_resolved(self):
        r = self.cleaned_data["resolved"].strip()

        if self.cleaned_data["resolved_checkbox"]:
            if not r:
                raise forms.ValidationError('Please provide explanation (like "Done") for why the milestone is no longer due.')
        else:
            r = ""

        return r


@role_required('WG Chair', 'Area Director', 'Secretariat')
def edit_milestones(request, acronym, milestone_set="current"):
    # milestones_set + needs_review: we have several paths into this view
    #  AD/Secr. -> all actions on current + add new
    #  group chair -> limited actions on current + add new for review
    #  (re)charter -> all actions on existing in state charter + add new in state charter
    #
    # For charters we store the history on the charter document to not confuse people.

    login = request.user.get_profile()

    group = get_object_or_404(Group, acronym=acronym)

    needs_review = False
    if not has_role(request.user, ("Area Director", "Secretariat")):
        if group.role_set.filter(name="chair", person=login):
            if milestone_set == "current":
                needs_review = True
        else:
            return HttpResponseForbidden("You are not chair of this group.")

    if milestone_set == "current":
        title = "Edit milestones for %s %s" % (group.acronym, group.type.name)
        milestones = group.groupmilestone_set.filter(state__in=("active", "review"))
    elif milestone_set == "charter":
        title = "Edit charter milestones for %s %s" % (group.acronym, group.type.name)
        milestones = group.groupmilestone_set.filter(state="charter")

    forms = []

    milestones_dict = dict((str(m.id), m) for m in milestones)

    def add_event(m, desc):
        if milestone_set == "charter":
            DocEvent.objects.create(doc=group.charter, type="changed_charter_milestone",
                                    by=login, desc=desc)
        else:
            MilestoneGroupEvent.objects.create(group=group, type="changed_milestone",
                                               by=login, desc=desc, milestone=m)

    finished_milestone_text = "Done"

    form_errors = False

    if request.method == 'POST':
        for prefix in request.POST.getlist("prefix"):
            if not prefix: # empty form
                continue

            # new milestones have non-existing ids so instance end up as None
            instance = milestones_dict.get(request.POST.get(prefix + "-id", ""), None)
            f = MilestoneForm(request.POST, prefix=prefix, instance=instance,
                              needs_review=needs_review)
            forms.append(f)

            form_errors = form_errors or not f.is_valid()

        if not form_errors:
            for f in forms:
                c = f.cleaned_data

                if f.milestone:
                    m = f.milestone

                    named_milestone = 'milestone "%s"' % m.desc
                    if milestone_set == "charter":
                        named_milestone = "charter " + named_milestone

                    if c["delete"]:
                        save_milestone_in_history(m)

                        m.state_id = "deleted"
                        m.save()

                        add_event(m, 'Deleted %s' % named_milestone)

                        continue

                    # compute changes
                    history = None

                    changes = ['Changed %s' % named_milestone]

                    if m.state_id == "review" and not needs_review and c["accept"]:
                        if not history:
                            history = save_milestone_in_history(m)
                        m.state_id = "active"
                        changes.append("changed state from review to active")


                    if c["desc"] != m.desc and not needs_review:
                        if not history:
                            history = save_milestone_in_history(m)
                        m.desc = c["desc"]
                        changes.append('changed description to "%s"' % m.desc)

                    if c["due"] != m.due:
                        if not history:
                            history = save_milestone_in_history(m)
                        m.due = c["due"]
                        changes.append('changed due date to %s' % m.due.strftime("%Y-%m-%d"))

                    resolved = c["resolved"]
                    if resolved != m.resolved:
                        if resolved and not m.resolved:
                            changes.append('resolved as "%s"' % resolved)
                        elif not resolved and m.resolved:
                            changes.append("reverted to not being resolved")
                        elif resolved and m.resolved:
                            changes.append('changed resolution to "%s"' % resolved)

                        if not history:
                            history = save_milestone_in_history(m)

                        m.resolved = resolved

                    new_docs = set(c["docs"])
                    old_docs = set(m.docs.all())
                    if new_docs != old_docs:
                        added = new_docs - old_docs
                        if added:
                            changes.append('added %s to milestone' % ", ".join(d.name for d in added))

                        removed = old_docs - new_docs
                        if removed:
                            changes.append('removed %s from milestone' % ", ".join(d.name for d in removed))

                        if not history:
                            history = save_milestone_in_history(m)

                        m.docs = new_docs

                    if len(changes) > 1:
                        add_event(m, ", ".join(changes))

                        m.save()

                else: # new milestone
                    m = GroupMilestone()
                    m.group = group
                    if milestone_set == "current":
                        if needs_review:
                            m.state = GroupMilestoneStateName.objects.get(slug="review")
                        else:
                            m.state = GroupMilestoneStateName.objects.get(slug="active")
                    elif milestone_set == "charter":
                        m.state = GroupMilestoneStateName.objects.get(slug="charter")
                    m.desc = c["desc"]
                    m.due = c["due"]
                    m.resolved = c["resolved"]
                    m.save()

                    m.docs = c["docs"]

                    named_milestone = 'milestone "%s"' % m.desc
                    if milestone_set == "charter":
                        named_milestone = "charter " + named_milestone

                    if m.state_id in ("active", "charter"):
                        add_event(m, 'Added %s, due %s' % (named_milestone, m.due.strftime("%Y-%m-%d")))
                    elif m.state_id == "review":
                        add_event(m, 'Added %s for review, due %s' % (named_milestone, m.due.strftime("%Y-%m-%d")))

            if milestone_set == "charter":
                return redirect('doc_view', name=group.charter.canonical_name())
            else:
                return redirect('wg_charter', acronym=group.acronym)
    else:
        for m in milestones:
            forms.append(MilestoneForm(instance=m, needs_review=needs_review))

    can_reset = milestone_set == "charter" and get_chartering_type(group.charter) == "rechartering"

    empty_form = MilestoneForm(needs_review=needs_review)

    return render_to_response('wginfo/edit_milestones.html',
                              dict(group=group,
                                   title=title,
                                   forms=forms,
                                   form_errors=form_errors,
                                   empty_form=empty_form,
                                   milestone_set=milestone_set,
                                   finished_milestone_text=finished_milestone_text,
                                   needs_review=needs_review,
                                   can_reset=can_reset),
                              context_instance=RequestContext(request))

@role_required('WG Chair', 'Area Director', 'Secretariat')
def reset_charter_milestones(request, acronym):
    """Reset charter milestones to the currently in-use milestones."""
    login = request.user.get_profile()

    group = get_object_or_404(Group, acronym=acronym)

    if (not has_role(request.user, ("Area Director", "Secretariat")) and
        not group.role_set.filter(name="chair", person=login)):
        return HttpResponseForbidden("You are not chair of this group.")

    current_milestones = group.groupmilestone_set.filter(state="active")
    charter_milestones = group.groupmilestone_set.filter(state="charter")

    if request.method == 'POST':
        try:
            milestone_ids = [int(v) for v in request.POST.getlist("milestone")]
        except ValueError as e:
            return HttpResponseBadRequest("errror in list of ids - %s" % e)

        # delete existing
        for m in charter_milestones:
            save_milestone_in_history(m)

            m.state_id = "deleted"
            m.save()

            DocEvent.objects.create(type="changed_charter_milestone",
                                    doc=group.charter,
                                    desc='Deleted milestone "%s"' % m.desc,
                                    by=login,
                                    )

        # add current
        for m in current_milestones.filter(id__in=milestone_ids):
            m = GroupMilestone.objects.create(group=m.group,
                                              state_id="charter",
                                              desc=m.desc,
                                              due=m.due,
                                              resolved=m.resolved,
                                              )
            m.docs = m.docs.all()

            DocEvent.objects.create(type="changed_charter_milestone",
                                    doc=group.charter,
                                    desc='Added milestone "%s", due %s, from current group milestones' % (m.desc, m.due.strftime("%Y-%m-%d")),
                                    by=login,
                                    )


        return redirect('wg_edit_charter_milestones', acronym=group.acronym)

    return render_to_response('wginfo/reset_charter_milestones.html',
                              dict(group=group,
                                   charter_milestones=charter_milestones,
                                   current_milestones=current_milestones,
                                   ),
                              context_instance=RequestContext(request))


def ajax_search_docs(request, acronym):
    docs = Document.objects.filter(name__icontains=request.GET.get('q',''), group__acronym=acronym, type="draft").order_by('name').distinct()[:20]
    return HttpResponse(json_doc_names(docs), mimetype='application/json')
