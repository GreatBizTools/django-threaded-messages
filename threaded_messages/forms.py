import settings as sendgrid_settings
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectMultipleWidget

from .models import *
from .fields import CommaSeparatedUserField
from .utils import reply_to_thread, now
from .signals import message_composed

from tms.models import Classroom,Trainee

if sendgrid_settings.THREADED_MESSAGES_USE_SENDGRID:
    from sendgrid_parse_api.utils import create_reply_email


notification = None
if "pinax.notifications" in settings.INSTALLED_APPS:
    from pinax.notifications import models as notification
    print "notification set in forms.py:", notification


class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = CommaSeparatedUserField(label=_(u"Recipients"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols': '55'}))

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        self.fields['recipient'].widget = AutoCompleteSelectMultipleWidget('all')
        self.fields['recipient'].widget.attrs.update({'placeholder':'Search by first name, last name, or class number', 'style': 'width: 95.5%;'})
        self.fields['subject'].widget.attrs.update({'style': 'width: 98.75%'})
        self.fields['body'].widget = CKEditorWidget(config_name='default')
        self.fields['body'].widget.attrs.update({'style': 'width: 100%'})
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter

    def save(self, sender, send=True):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        recipients_cleaned = []
        for r in recipients:
            if r.split("_")[0]==u"class":
                class_id = int(r.split("_")[1])
                classroom_object = Classroom.objects.get(id=class_id)
                trainers_ids = [int(trainer['id']) for trainer in classroom_object.trainers.values()]

                trainee_ids = [int(trainee.user.id) for trainee in Trainee.objects.filter(classroom_id=class_id)]
                recipients_cleaned.extend(trainers_ids)
                recipients_cleaned.extend(trainee_ids)
            else:
                user_id = int(r.split("_")[1])
                recipients_cleaned.append(user_id)
        recipients_cleaned = list(set(recipients_cleaned))
        recipients = [User.objects.get(pk=key) for key in recipients_cleaned]
        new_message = Message.objects.create(body=body, sender=sender)

        thread = Thread.objects.create(subject=subject,
                                       latest_msg=new_message,
                                       creator=sender)
        thread.all_msgs.add(new_message)

        for recipient in recipients:
            Participant.objects.create(thread=thread, user=recipient)

        (sender_part, created) = Participant.objects.get_or_create(thread=thread, user=sender)
        sender_part.replied_at = sender_part.read_at = now()
        sender_part.save()

        thread.save()  # save this last, since this updates the search index

        message_composed.send(sender=Message,
                              message=new_message,
                              recipients=recipients)

        #send notifications
        print "notification within def save: ", notification

        if send and notification:
            if sendgrid_settings.THREADED_MESSAGES_USE_SENDGRID:
                for r in recipients:
                    reply_email = create_reply_email(sendgrid_settings.THREADED_MESSAGES_ID, r, thread)
                    notification.send(recipients, "received_email",
                                        {"thread": thread,
                                         "message": new_message}, sender=sender,
                                        from_email=reply_email.get_from_email(),
                                        headers={'Reply-To': reply_email.get_reply_to_email()})
            else:
                notification.send(recipients, "received_email",
                                        {"thread": thread,
                                         "message": new_message}, sender=sender)

        return (thread, new_message)


class ReplyForm(forms.Form):
    """
    A simple default form for private messages.
    """
    body = forms.CharField(label=_(u"Reply"))

    def save(self, sender, thread):
        body = self.cleaned_data['body']
        return reply_to_thread(thread, sender, body)

class NewReplyForm(ReplyForm):
      def __init__(self, *args, **kwargs):
        super(NewReplyForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget = CKEditorWidget()
        self.fields['body'].widget.attrs.update({'id': 'reply-body', 'name' : 'editor1'})
