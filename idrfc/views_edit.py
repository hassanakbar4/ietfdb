import re, os
from datetime import datetime, date, time
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import forms
from django.utils.html import strip_tags

from ietf.ietfauth.decorators import group_required
from ietf.idtracker.models import InternetDraft, IDInternal, IDState, IDSubState, IDNextState, DocumentComment, format_document_state, IESGLogin
#from ietf.idrfc.idrfc_wrapper import BallotWrapper, IdWrapper, RfcWrapper
from ietf import settings
from ietf.utils.mail import send_mail

class ChangeStateForm(forms.Form):
    state = forms.ModelChoiceField(IDState.objects.all(), empty_label=None, required=True)
    substate = forms.ModelChoiceField(IDSubState.objects.all(), required=False)

def send_doc_state_changed_email(request, doc, text):
    to = [x.strip() for x in doc.idinternal.state_change_notice_to.replace(';', ',').split(',')]
    send_mail(request, to, None,
              "ID Tracker State Update Notice: %s" % doc.filename,
              "idrfc/state_changed_email.txt",
              dict(text=text,
                   url=request.build_absolute_uri(doc.idinternal.get_absolute_url())))
    
    
@group_required('Area_Director','Secretariat')
def change_state(request, name):
    doc = get_object_or_404(InternetDraft, filename=name)

    user = IESGLogin.objects.get(login_name=request.user.username)
    
    if request.method == 'POST':
        form = ChangeStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state']
            sub_state = form.cleaned_data['substate']
            internal = doc.idinternal
            if state != internal.cur_state or sub_state != internal.cur_sub_state:
                internal.change_state(state, sub_state)

                change = u"State changed to <b>%s</b> from <b>%s</b> by <b>%s</b>" % (internal.docstate(), format_document_state(internal.prev_state, internal.prev_sub_state), user)
                
                c = DocumentComment()
                c.document = internal
                c.public_flag = True
                c.version = doc.revision_display()
                c.comment_text = change
                c.created_by = user
                c.result_state = internal.cur_state
                c.origin_state = internal.prev_state
                c.rfc_flag = internal.rfc_flag
                c.save()

                internal.event_date = date.today()
                internal.save()

                send_doc_state_changed_email(request, doc, strip_tags(change))
                
            return HttpResponseRedirect(internal.get_absolute_url())

    else:
        form = ChangeStateForm(initial=dict(state=doc.idinternal.cur_state_id,
                                            substate=doc.idinternal.cur_sub_state_id))

    next_states = IDNextState.objects.filter(cur_state=doc.idinternal.cur_state)

    
    # FIXME: last_call_requested

    return render_to_response('idrfc/edit_state.html',
                              dict(form=form,
                                   next_states=next_states),
                              context_instance=RequestContext(request))
    
