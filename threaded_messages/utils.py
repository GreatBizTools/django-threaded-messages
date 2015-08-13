# -*- coding:utf-8 -*-
import datetime
import re

from django.conf import settings
from django.core.cache import cache
from django.template import Context
from django.template.loader import get_template

from . import settings as tm_settings


if "pinax.notifications" in settings.INSTALLED_APPS:
    from pinax.notifications import models as notification
else:
    notification=None

# favour django-mailer but fall back to django.core.mail
if tm_settings.THREADED_MESSAGES_USE_SENDGRID:
    import sendgrid_parse_api

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now


def fill_count_cache(user):
    from .models import inbox_count_for
    cache.set(tm_settings.INBOX_COUNT_CACHE % user.pk,
              inbox_count_for(user), tm_settings.INBOX_COUNT_CACHE_TIME)


def open_message_thread(recipients, subject, template,
                        sender, context={}, send=True, message=None):
    body = ''
    if template:
        t = get_template(template)
        body = t.render(Context(context))
    else:
        body = message

    from forms import ComposeForm  # temporary here to remove circular dependence
    compose_form = ComposeForm(data={
        "recipient": recipients,
        "subject": subject,
        "body": body
    })
    if compose_form.is_valid():
        (thread, new_message) = compose_form.save(sender=sender, send=send)

    return (thread, new_message)


def reply_to_thread(thread, sender, body):
    from .models import Message, Participant
    new_message = Message.objects.create(body=body, sender=sender)
    new_message.parent_msg = thread.latest_msg
    thread.latest_msg = new_message
    thread.all_msgs.add(new_message)
    thread.replied = True
    thread.save()
    new_message.save()

    recipients = []
    for participant in thread.participants.all():
        participant.deleted_at = None
        participant.save()
        if sender != participant.user:  # dont send emails to the sender!
            recipients.append(participant.user)

    sender_part = Participant.objects.get(thread=thread, user=sender)
    sender_part.replied_at = sender_part.read_at = now()
    sender_part.save()

    invalidate_count_cache(Message, new_message)

    if notification:
        for r in recipients:
            if tm_settings.THREADED_MESSAGES_USE_SENDGRID:
                reply_email = sendgrid_parse_api.utils.create_reply_email(tm_settings.THREADED_MESSAGES_ID, r, thread)
                notification.send(recipients, "received_email",
                                        {"thread": thread,
                                         "message": new_message}, sender=sender,
                                        from_email=reply_email.get_from_email(),
                                        headers={'Reply-To': reply_email.get_reply_to_email()})
            else:
                notification.send([r], "received_email",
                                    {"thread": thread,
                                     "message": new_message}, sender=sender)

    return (thread, new_message)


def get_lines(body):
    body = body.replace('\r', ' ')
    lines = [x.strip() for x in body.splitlines(True)]
    return lines


def strip_mail(body):

    custom_line_no = None

    lines = get_lines(body)

    has_signature = False
    for l in lines:
        if l.strip().startswith('>'):
            has_signature = True

    # strip signature -- only if there is a signature. otherwise all is stripped
    if has_signature:
        for l in reversed(lines):
            lines.remove(l)
            if l.strip().startswith('>'):
                break

    # strip quotes
    for i, l in enumerate(lines):
        if l.lstrip().startswith('>'):
            if not custom_line_no:
                custom_line_no = i - 1
                popme = custom_line_no
                while not lines[popme]:
                    lines.pop(popme)
                    popme -= 1
                if re.search(r'^.*?([0-1][0-9]|[2][0-3]):([0-5][0-9]).*?$', lines[popme]) or re.search(r'[\w-]+@([\w-]+\.)+[\w-]+', lines[popme]):
                    lines.pop(popme)
                break

    stripped_lines = [s for s in lines if not s.lstrip().startswith('>')]

    # strip last empty string in the list if it exists
    if not stripped_lines[-1]:
        stripped_lines.pop()

    # stripped message
    return ('\n').join(stripped_lines)


def invalidate_count_cache(sender, message, recipients=None, **kwargs):
    for thread in message.thread.select_related().all():
        for participant in thread.participants.exclude(user=message.sender):
            fill_count_cache(participant.user)
