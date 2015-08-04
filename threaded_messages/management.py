from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals

if "pinax.notifications" in settings.INSTALLED_APPS:
    from pinax.notifications import models as notification
    from pinax.notifications.models import NoticeType

    def create_notice_types(sender, **kwargs):
        if "pinax.notifications" in settings.INSTALLED_APPS:
            print "Creating notices for myapp"
            NoticeType.create("received_email", _("Private messages"), _("(this is highly recommended)"))
            signals.post_syncdb.connect(create_notice_types, sender=notification)
        else:
            print "Skipping creation of NoticeTypes (Threaded Messages) as notification app not found"
