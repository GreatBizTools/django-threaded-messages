import logging

from django.utils.html import strip_tags

from . import settings as sendgrid_settings
from .signals import message_composed

logger = logging.getLogger('threaded_messages')

if sendgrid_settings.THREADED_MESSAGES_USE_SENDGRID:
    from sendgrid_parse_api.signals import email_received
else:
    email_received = None


def signal_received_email(sender, sma, app_id, html, text, from_field, **kwargs):
    from .utils import reply_to_thread, strip_mail
    logger.debug("Sendgrid signal receive: %s, %s, %s, %s, %s, %s" % (sender, sma, app_id,
                                                                    html, repr(text), from_field))
    if app_id == sendgrid_settings.THREADED_MESSAGES_ID:
        body = ''

        if text:
            body = text

        if not body:
            body = html

        if body:
            body = strip_tags(body)
            body = strip_mail(body)
            thread = sma.content_object
            reply_to_thread(thread, sma.user, body)


def start_listening():
    if email_received:
        logger.debug("Sendgrid start listening")
        email_received.connect(signal_received_email, dispatch_uid="thm_reply")

    from .utils import invalidate_count_cache
    message_composed.connect(invalidate_count_cache, dispatch_uid="thm_composed")
