# expiry of Internet Drafts

from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q

import datetime, os, shutil, glob, re

from ietf.idtracker.models import InternetDraft, IDDates, IDStatus, IDState, DocumentComment, IDAuthor,WGChair
from ietf.utils.mail import send_mail, send_mail_subj
from ietf.idrfc.utils import log_state_changed, add_document_comment
from doc.models import Document, DocEvent, save_document_in_history
from name.models import IesgDocStateName, DocStateName, DocInfoTagName
from person.models import Person, Email

INTERNET_DRAFT_DAYS_TO_EXPIRE = 185

def in_id_expire_freeze(when=None):
    if when == None:
        when = datetime.datetime.now()
        
    d = IDDates.objects.get(id=IDDates.SECOND_CUT_OFF).date
    # for some reason, the old Perl code started at 9 am
    second_cut_off = datetime.datetime.combine(d, datetime.time(9, 0))
    
    d = IDDates.objects.get(id=IDDates.IETF_MONDAY).date
    ietf_monday = datetime.datetime.combine(d, datetime.time(0, 0))
    
    return second_cut_off <= when < ietf_monday

def document_expires(doc):
    e = doc.latest_event(type__in=("completed_resurrect", "new_revision"))
    if e:
        return e.time + datetime.timedelta(days=INTERNET_DRAFT_DAYS_TO_EXPIRE)
    else:
        return None

def expirable_documents():
    return Document.objects.filter(state="active").exclude(tags="rfc-rev").filter(Q(iesg_state=None) | Q(iesg_state__order__gte=42))

def get_soon_to_expire_ids(days):
    start_date = datetime.date.today() - datetime.timedelta(InternetDraft.DAYS_TO_EXPIRE - 1)
    end_date = start_date + datetime.timedelta(days - 1)
    
    for d in InternetDraft.objects.filter(revision_date__gte=start_date,revision_date__lte=end_date,status__status='Active'):
        if d.can_expire():
            yield d

def get_soon_to_expire_idsREDESIGN(days):
    start_date = datetime.date.today() - datetime.timedelta(1)
    end_date = start_date + datetime.timedelta(days - 1)
    
    for d in expirable_documents():
        t = document_expires(d)
        if t and start_date <= t.date() <= end_date:
            yield d

def get_expired_ids():
    cut_off = datetime.date.today() - datetime.timedelta(days=InternetDraft.DAYS_TO_EXPIRE)

    return InternetDraft.objects.filter(
        revision_date__lte=cut_off,
        status__status="Active",
        review_by_rfc_editor=0).filter(
        Q(idinternal=None) | Q(idinternal__cur_state__document_state_id__gte=42))

def get_expired_idsREDESIGN():
    today = datetime.date.today()

    for d in expirable_documents():
        t = document_expires(d)
        if t and t.date() <= today:
            yield d

def send_expire_warning_for_id(doc):
    expiration = doc.expiration()
    # Todo:
    #second_cutoff = IDDates.objects.get(date_id=2)
    #ietf_monday = IDDates.objects.get(date_id=3)
    #freeze_delta = ietf_monday - second_cutoff
    #   # The I-D expiration job doesn't run while submissions are frozen.
    #   if ietf_monday > expiration > second_cutoff:
    #       expiration += freeze_delta
    
    authors = doc.authors.all()
    to_addrs = [author.email() for author in authors if author.email()]
    cc_addrs = None
    if doc.group.acronym != 'none':
        cc_addrs = [chair.person.email() for chair in WGChair.objects.filter(group_acronym=doc.group)]

    if to_addrs or cc_addrs:
        send_mail_subj(None, to_addrs, None, 'notify_expirations/subject.txt', 'notify_expirations/body.txt', 
                   {
                      'draft':doc,
                      'expiration':expiration,
                   },
                   cc_addrs)

def send_expire_warning_for_idREDESIGN(doc):
    expiration = document_expires(doc).date()

    to = [e.formatted_email() for e in doc.authors.all() if not e.address.startswith("unknown-email")]
    cc = None
    if doc.group.type_id != "individ":
        cc = [e.formatted_email() for e in Email.objects.filter(role__group=doc.group, role__name="chair") if not e.address.startswith("unknown-email")]

    state = doc.iesg_state.name if doc.iesg_state else "I-D Exists"
        
    frm = None
    request = None
    if to or cc:
        send_mail(request, to, frm,
                  u"Expiration impending: %s" % doc.file_tag(),
                  "idrfc/expire_warning_email.txt",
                  dict(doc=doc,
                       state=state,
                       expiration=expiration
                       ),
                  cc=cc)

def send_expire_notice_for_id(doc):
    doc.dunn_sent_date = datetime.date.today()
    doc.save()

    if not doc.idinternal:
        return
    
    request = None
    to = u"%s <%s>" % doc.idinternal.job_owner.person.email()
    send_mail(request, to,
              "I-D Expiring System <ietf-secretariat-reply@ietf.org>",
              u"I-D was expired %s" % doc.file_tag(),
              "idrfc/id_expired_email.txt",
              dict(doc=doc,
                   state=doc.idstate()))

def send_expire_notice_for_idREDESIGN(doc):
    if not doc.ad:
        return

    state = doc.iesg_state.name if doc.iesg_state else "I-D Exists"
    
    request = None
    to = doc.ad.formatted_email()
    send_mail(request, to,
              "I-D Expiring System <ietf-secretariat-reply@ietf.org>",
              u"I-D was expired %s" % doc.file_tag(),
              "idrfc/id_expired_email.txt",
              dict(doc=doc,
                   state=state,
                   ))

def expire_id(doc):
    def move_file(f):
        src = os.path.join(settings.INTERNET_DRAFT_PATH, f)
        dst = os.path.join(settings.INTERNET_DRAFT_ARCHIVE_DIR, f)

        if os.path.exists(src):
            shutil.move(src, dst)

    move_file("%s-%s.txt" % (doc.filename, doc.revision_display()))
    move_file("%s-%s.ps" % (doc.filename, doc.revision_display()))
    move_file("%s-%s.pdf" % (doc.filename, doc.revision_display()))

    new_revision = "%02d" % (int(doc.revision) + 1)

    new_file = open(os.path.join(settings.INTERNET_DRAFT_PATH, "%s-%s.txt" % (doc.filename, new_revision)), 'w')
    txt = render_to_string("idrfc/expire_text.txt",
                           dict(doc=doc,
                                authors=[a.person.email() for a in doc.authors.all()],
                                expire_days=InternetDraft.DAYS_TO_EXPIRE))          
    new_file.write(txt)
    new_file.close()
    
    doc.revision = new_revision
    doc.expiration_date = datetime.date.today()
    doc.last_modified_date = datetime.date.today()
    doc.status = IDStatus.objects.get(status="Expired")
    doc.save()

    if doc.idinternal:
        if doc.idinternal.cur_state_id != IDState.DEAD:
            doc.idinternal.change_state(IDState.objects.get(document_state_id=IDState.DEAD), None)
            log_state_changed(None, doc, "system")

        add_document_comment(None, doc, "Document is expired by system")

def expire_idREDESIGN(doc):
    system = Person.objects.get(name="(System)")

    # clean up files
    def move_file(f):
        src = os.path.join(settings.INTERNET_DRAFT_PATH, f)
        dst = os.path.join(settings.INTERNET_DRAFT_ARCHIVE_DIR, f)

        if os.path.exists(src):
            shutil.move(src, dst)

    file_types = ['txt', 'ps', 'pdf']
    for t in file_types:
        move_file("%s-%s.%s" % (doc.name, doc.rev, t))

    # make tombstone
    new_revision = "%02d" % (int(doc.rev) + 1)

    new_file = open(os.path.join(settings.INTERNET_DRAFT_PATH, "%s-%s.txt" % (doc.name, new_revision)), 'w')
    txt = render_to_string("idrfc/expire_textREDESIGN.txt",
                           dict(doc=doc,
                                authors=[(e.get_name(), e.address) for e in doc.authors.all()],
                                expire_days=InternetDraft.DAYS_TO_EXPIRE))
    new_file.write(txt)
    new_file.close()
    
    # now change the states
    
    save_document_in_history(doc)
    if doc.latest_event(type='started_iesg_process'):
        dead_state = IesgDocStateName.objects.get(slug="dead")
        if doc.iesg_state != dead_state:
            prev = doc.iesg_state
            doc.iesg_state = dead_state
            log_state_changed(None, doc, system, prev)

        e = DocEvent(doc=doc, by=system)
        e.type = "expired_document"
        e.desc = "Document has expired"
        e.save()
    
    doc.rev = new_revision # FIXME: incrementing the revision like this is messed up
    doc.state = DocStateName.objects.get(slug="expired")
    doc.time = datetime.datetime.now()
    doc.save()

def clean_up_id_files():
    """Move unidentified and old files out of the Internet Draft directory."""
    cut_off = datetime.date.today() - datetime.timedelta(days=InternetDraft.DAYS_TO_EXPIRE)

    pattern = os.path.join(settings.INTERNET_DRAFT_PATH, "draft-*.*")
    files = []
    filename_re = re.compile('^(.*)-(\d+)$')
    for path in glob.glob(pattern):
        basename = os.path.basename(path)
        stem, ext = os.path.splitext(basename)
        match = filename_re.search(stem)
        if not match:
            filename, revision = ("UNKNOWN", "00")
        else:
            filename, revision = match.groups()

        def move_file_to(subdir):
            shutil.move(path,
                        os.path.join(settings.INTERNET_DRAFT_ARCHIVE_DIR, subdir, basename))
            
        try:
            doc = InternetDraft.objects.get(filename=filename, revision=revision)

            if doc.status_id == 3:
                if ext != ".txt":
                    move_file_to("unknown_ids")
            elif doc.status_id in (2, 4, 5, 6) and doc.expiration_date and doc.expiration_date < cut_off:
                if os.path.getsize(path) < 1500:
                    move_file_to("deleted_tombstones")
                    # revert version after having deleted tombstone
                    doc.revision = "%02d" % (int(revision) - 1)
                    doc.expired_tombstone = True
                    doc.save()
                else:
                    move_file_to("expired_without_tombstone")
            
        except InternetDraft.DoesNotExist:
            move_file_to("unknown_ids")

def clean_up_id_filesREDESIGN():
    """Move unidentified and old files out of the Internet Draft directory."""
    cut_off = datetime.date.today() - datetime.timedelta(days=INTERNET_DRAFT_DAYS_TO_EXPIRE)

    pattern = os.path.join(settings.INTERNET_DRAFT_PATH, "draft-*.*")
    files = []
    filename_re = re.compile('^(.*)-(\d+)$')
    for path in glob.glob(pattern):
        basename = os.path.basename(path)
        stem, ext = os.path.splitext(basename)
        match = filename_re.search(stem)
        if not match:
            filename, revision = ("UNKNOWN", "00")
        else:
            filename, revision = match.groups()

        def move_file_to(subdir):
            shutil.move(path,
                        os.path.join(settings.INTERNET_DRAFT_ARCHIVE_DIR, subdir, basename))
            
        try:
            doc = Document.objects.get(name=filename, rev=revision)

            if doc.state_id == "rfc":
                if ext != ".txt":
                    move_file_to("unknown_ids")
            elif doc.state_id in ("expired", "auth-rm", "repl", "ietf-rm"):
                e = doc.latest_event(type__in=('expired_document', 'new_revision', "completed_resurrect"))
                expiration_date = e.time.date() if e and e.type == "expired_document" else None

                if expiration_date and expiration_date < cut_off:
                    if os.path.getsize(path) < 1500:
                        move_file_to("deleted_tombstones")
                        # revert version after having deleted tombstone
                        doc.rev = "%02d" % (int(revision) - 1) # FIXME: messed up
                        doc.save()
                        doc.tags.add(DocInfoTagName.objects.get(slug='exp-tomb'))
                    else:
                        move_file_to("expired_without_tombstone")
            
        except Document.DoesNotExist:
            move_file_to("unknown_ids")

if settings.USE_DB_REDESIGN_PROXY_CLASSES:
    get_soon_to_expire_ids = get_soon_to_expire_idsREDESIGN
    get_expired_ids = get_expired_idsREDESIGN
    send_expire_warning_for_id = send_expire_warning_for_idREDESIGN
    send_expire_notice_for_id = send_expire_notice_for_idREDESIGN
    expire_id = expire_idREDESIGN
    clean_up_id_files = clean_up_id_filesREDESIGN
