# Copyright The IETF Trust 2007, All Rights Reserved

from email.Utils import make_msgid, formatdate, formataddr, parseaddr, getaddresses
from email.MIMEText import MIMEText
from email.MIMEMessage import MIMEMessage
from email.MIMEMultipart import MIMEMultipart
from email import message_from_string
import smtplib
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.template import Context,RequestContext
import ietf
from ietf.utils import log
import sys
import time
import copy

# Testing mode:
# import ietf.utils.mail
# ietf.utils.mail.test_mode = True
# ... send some mail ...
# ... inspect ietf.utils.mail.outbox ...
# ... call ietf.utils.mail.empty_outbox() ...
test_mode = False
outbox = []

def empty_outbox():
     outbox[:] = []

def add_headers(msg):
    if not(msg.has_key('Message-ID')):
	msg['Message-ID'] = make_msgid('idtracker')
    if not(msg.has_key('Date')):
	msg['Date'] = formatdate(time.time(), True)
    if not(msg.has_key('From')):
	msg['From'] = settings.DEFAULT_FROM_EMAIL
    return msg

def send_smtp(msg, bcc=None):
    '''
    Send a Message via SMTP, based on the django email server settings.
    The destination list will be taken from the To:/Cc: headers in the
    Message.  The From address will be used if present or will default
    to the django setting DEFAULT_FROM_EMAIL

    If someone has set test_mode=True, then just append the msg to
    the outbox.
    '''
    add_headers(msg)
    (fname, frm) = parseaddr(msg.get('From'))
    addrlist = msg.get_all('To') + msg.get_all('Cc', [])
    if bcc:
        addrlist += [bcc]
    to = [addr for name, addr in getaddresses(addrlist)]
    if not to:
        log("No addressees for email from '%s', subject '%s'.  Nothing sent." % (frm, msg.get('Subject', '[no subject]')))
    else:
        if test_mode:
            outbox.append(msg)
            return
        server = None
        try:
            server = smtplib.SMTP()
            if settings.DEBUG:
                server.set_debuglevel(1)
            server.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                server.ehlo()
                if 'starttls' not in server.esmtp_features:
                    raise ImproperlyConfigured('password configured but starttls not supported')
                (retval, retmsg) = server.starttls()
                if retval != 220:
                    raise ImproperlyConfigured('password configured but tls failed: %d %s' % ( retval, retmsg ))
                # Send a new EHLO, since without TLS the server might not
                # advertise the AUTH capability.
                server.ehlo()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(frm, to, msg.as_string())
            # note: should pay attention to the return code, as it may
            # indicate that someone didn't get the email.
        except:
            if server:
                server.quit()
            # need to improve log message
            log("got exception '%s' (%s) trying to send email from '%s' to %s subject '%s'" % (sys.exc_info()[0], sys.exc_info()[1], frm, to, msg.get('Subject', '[no subject]')))
            if isinstance(sys.exc_info()[0], smtplib.SMTPException):
                raise
            else:
                raise smtplib.SMTPException({'really': sys.exc_info()[0], 'value': sys.exc_info()[1], 'tb': sys.exc_info()[2]})
        server.quit()
        log("sent email from '%s' to %s subject '%s'" % (frm, to, msg.get('Subject', '[no subject]')))
    
def copy_email(msg, to, toUser=False):
    '''
    Send a copy of the given email message to the given recipient.
    '''
    add_headers(msg)
    new = MIMEMultipart()
    # get info for first part.
    # Mode: if it's production, then "copy of a message", otherwise
    #  "this is a message that would have been sent from"
    # hostname?
    # django settings if debugging?
    # Should this be a template?
    if settings.SERVER_MODE == 'production':
	explanation = "This is a copy of a message sent from the I-D tracker."
    elif settings.SERVER_MODE == 'test' and toUser:
	explanation = "The attached message was generated by an instance of the tracker\nin test mode.  It is being sent to you because you, or someone acting\non your behalf, is testing the system.  If you do not recognize\nthis action, please accept our apologies and do not be concerned as\nthe action is being taken in a test context."
    else:
	explanation = "The attached message would have been sent, but the tracker is in %s mode.\nIt was not sent to anybody." % settings.SERVER_MODE
    new.attach(MIMEText(explanation + "\n\n"))
    new.attach(MIMEMessage(msg))
    # Overwrite the From: header, so that the copy from a development or
    # test server doesn't look like spam.
    new['From'] = settings.DEFAULT_FROM_EMAIL
    new['Subject'] = '[Django %s] %s' % (settings.SERVER_MODE, msg.get('Subject', '[no subject]'))
    new['To'] = to
    send_smtp(new)

def mail_context(request):
    if request:
        return RequestContext(request)
    else:
        return Context()
  
def send_mail_subj(request, to, frm, stemplate, template, context, *args, **kwargs):
    '''
    Send an email message, exactly as send_mail(), but the
    subject field is a template.
    '''
    subject = render_to_string(stemplate, context, context_instance=mail_context(request)).replace("\n"," ").strip()
    return send_mail(request, to, frm, subject, template, context, *args, **kwargs)

def send_mail(request, to, frm, subject, template, context, *args, **kwargs):
    '''
    Send an email to the destination [list], with the given return
    address (or "None" to use the default in settings.py).
    The body is a text/plain rendering of the template with the context.
    extra is a dict of extra headers to add.
    '''
    txt = render_to_string(template, context, context_instance=mail_context(request))
    return send_mail_text(request, to, frm, subject, txt, *args, **kwargs)


def send_mail_text(request, to, frm, subject, txt, cc=None, extra=None, toUser=False, bcc=None):
    """Send plain text message."""
    if isinstance(txt, unicode):
        msg = MIMEText(txt.encode('utf-8'), 'plain', 'UTF-8')
    else:
        msg = MIMEText(txt)
    send_mail_mime(request, to, frm, subject, msg, cc, extra, toUser, bcc)
        
def send_mail_mime(request, to, frm, subject, msg, cc=None, extra=None, toUser=False, bcc=None):
    """Send MIME message with content already filled in."""
    if isinstance(frm, tuple):
	frm = formataddr(frm)
    if isinstance(to, list) or isinstance(to, tuple):
        to = ", ".join([isinstance(addr, tuple) and formataddr(addr) or addr for addr in to if addr])
    if isinstance(cc, list) or isinstance(cc, tuple):
        cc = ", ".join([isinstance(addr, tuple) and formataddr(addr) or addr for addr in cc if addr])
    if frm:
	msg['From'] = frm
    msg['To'] = to
    if cc:
	msg['Cc'] = cc
    msg['Subject'] = subject
    msg['X-Test-IDTracker'] = (settings.SERVER_MODE == 'production') and 'no' or 'yes'
    msg['X-IETF-IDTracker'] = ietf.__version__
    if extra:
	for k, v in extra.items():
	    msg[k] = v
    if test_mode or settings.SERVER_MODE == 'production':
	send_smtp(msg, bcc)
    elif settings.SERVER_MODE == 'test':
	if toUser:
	    copy_email(msg, to, toUser=True)
	elif request and request.COOKIES.has_key( 'testmailcc' ):
	    copy_email(msg, request.COOKIES[ 'testmailcc' ])
    try:
	copy_to = settings.EMAIL_COPY_TO
    except AttributeError:
	copy_to = "ietf.tracker.archive+%s@gmail.com" % settings.SERVER_MODE
    if bcc:
        msg['X-Tracker-Bcc']=bcc
    if not test_mode: # if we're running automated tests, this copy is just annoying
        copy_email(msg, copy_to)

def send_mail_preformatted(request, preformatted):
    """Parse preformatted string containing mail with From:, To:, ...,
    and send it through the standard IETF mail interface (inserting
    extra headers as needed)."""
    msg = message_from_string(preformatted.encode("utf-8"))
    extra = copy.copy(msg)
    for key in ['To', 'From', 'Subject', ]:
        del extra[key]
    send_mail_text(request, msg['To'], msg["From"], msg["Subject"], msg.get_payload(), extra=extra)
