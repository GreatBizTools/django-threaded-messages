from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.db.models import F, Q

from json import dumps, loads

from .listeners import start_listening

from .settings import INBOX_MESSAGE_CACHE, INBOX_MESSAGE_CACHE_TIME



start_listening()


class MessageManager(models.Manager):

    def inbox_for(self, user, read=None, only_unreplied=None):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        inbox = self.filter(
            user=user,
            deleted_at__isnull=True,
        )
        if read != None:
            if read == True:
                # read messages have read_at set to a later value then last message of the thread
                inbox = inbox.exclude(read_at__isnull=True)\
                        .filter(read_at__gt=F("thread__latest_msg__sent_at"))
            else:
                # unread threads are the ones that either have not been read at all or before the last message arrived
                inbox = inbox.filter(Q(read_at__isnull=True)
                                    | Q(read_at__lt=F("thread__latest_msg__sent_at")))

        if only_unreplied != None:
            if only_unreplied == True:
                inbox = inbox.filter(Q(replied_at__isnull=True)
                                    | Q(replied_at__lt=F("thread__latest_msg__sent_at")))

        return inbox

    def outbox_for(self, user, read=None, only_unreplied=None):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.
        """
        outbox = self.filter(
            user=user,
            replied_at__isnull=False,
            deleted_at__isnull=True,

        )
        if read != None:
            if read == True:
                # read messages have read_at set to a later value then last message of the thread
                outbox = outbox.exclude(read_at__isnull=True)\
                            .filter(read_at__gt=F("thread__latest_msg__sent_at"))
            else:
                # unread threads are the ones that either have not been read at all or before the last message arrived
                outbox = outbox.filter(Q(read_at__isnull=True)
                                    | Q(read_at__lt=F("thread__latest_msg__sent_at")))

        if only_unreplied != None:
            if only_unreplied == True:
                inbox = outbox.filter(Q(replied_at__isnull=True)
                                    | Q(replied_at__lt=F("thread__latest_msg__sent_at")))

        return outbox


    def trash_for(self, user, read=None, only_unreplied=None):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        """
        trash = self.filter(
            user=user,
            deleted_at__isnull=False,
        )

        if read != None:
            if read == True:
                # read messages have read_at set to a later value then last message of the thread
                trash = trash.exclude(read_at__isnull=True)\
                            .filter(read_at__gt=F("thread__latest_msg__sent_at"))
            else:
                # unread threads are the ones that either have not been read at all or before the last message arrived
                trash = trash.filter(Q(read_at__isnull=True)
                                    | Q(read_at__lt=F("thread__latest_msg__sent_at")))

        if only_unreplied != None:
            if only_unreplied == True:
                trash = trash.filter(Q(replied_at__isnull=True)
                                    | Q(replied_at__lt=F("thread__latest_msg__sent_at")))

        return trash


class Message(models.Model):
    """
    A private message from user to user
    """
    body = models.TextField(_("body"))
    sender = models.ForeignKey(User, related_name='sent_messages', blank=True, null=True, verbose_name=_("sender"))
    parent_msg = models.ForeignKey('self', related_name='next_messages', blank=True, null=True, verbose_name=_("parent message"))
    sent_at = models.DateTimeField(_("sent at"), auto_now_add=True,
        db_index=True)

    def __unicode__(self):
        return "%s - %s" % (str(self.sender), self.sent_at)

    def save(self, **kwargs):
        if not self.id:
            from .utils import now
            self.sent_at = now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


class Thread(models.Model):
    """
    A linear conversation between two or more Users
    """
    subject = models.CharField(_("Subject"), max_length=120)
    latest_msg = models.ForeignKey(Message, related_name='thread_latest', verbose_name=_("Latest message"))
    all_msgs = models.ManyToManyField(Message, related_name='thread', verbose_name=_("Messages"))
    # the following fields are used to filter out messages that have not been replied to in the inbox
    creator = models.ForeignKey(User, related_name='created_threads', verbose_name=_("creator"))
    replied = models.BooleanField(editable=False, default=False)

    def __unicode__(self):
        return self.subject

    def get_absolute_url(self):
        return ('tm:messages_detail', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)

    class Meta:
        ordering = ['latest_msg']
        verbose_name = _("Thread")
        verbose_name_plural = _("Threads")


class Participant(models.Model):
    """
    Thread manager for each participant
    """
    thread = models.ForeignKey(Thread, related_name='participants', verbose_name=_("message thread"))
    user = models.ForeignKey(User, related_name='threads', verbose_name=_("participant users"))
    read_at = models.DateTimeField(_("read at"), null=True, blank=True,
        db_index=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True,
        db_index=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True, blank=True,
        db_index=True)

    objects = MessageManager()

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is None or self.read_at < self.thread.latest_msg.sent_at:
            return True
        return False

    def replied(self):
        """returns whether the recipient has replied the message or not"""
        if self.replied_at is None \
            or self.replied_at < self.thread.latest_msg.sent_at:
            return True
        return False

    def last_other_sender(self):
        """returns the last sender thats not the viewing user. if nobody
            besides you sent a message to the thread we take a random one
        """
        message = self.thread.all_msgs.exclude(sender=self.user)
        if message:
            return message[0].sender
        #else:
            # others = self.others()
            # if others:
            #     return others[0].user

        return None

    def others(self):
        """returns the other participants of the thread"""
        return self.thread.participants.exclude(user=self.user)

    def get_next(self):
        try:
            participation = Participant.objects.inbox_for(
                    self.user
                ).filter(
                    thread__latest_msg__sent_at__gt=self.thread.latest_msg.sent_at
                ).reverse()[0]
            return participation
        except:
            return None

    def get_previous(self):
        try:
            participation = Participant.objects.inbox_for(
                    self.user
                ).filter(
                    thread__latest_msg__sent_at__lt=self.thread.latest_msg.sent_at)[0]
            return participation
        except:
            return None

    def read_thread(self):
        """
        Marks thread as read and refill count cache
        """
        from .utils import fill_message_cache, now
        self.read_at = now()
        self.save()
        fill_message_cache(self.user)

    def unread_thread(self):
        from .utils import fill_message_cache
        self.read_at = None
        self.save()
        fill_message_cache(self.user)

    def __unicode__(self):
        return "%s - %s" % (str(self.user), self.thread.subject)

    class Meta:
        ordering = ['thread']
        verbose_name = _("participant")
        verbose_name_plural = _("participants")

def inbox_count_for(user):
    return Participant.objects.inbox_for(user, read=False).count()


def inbox_messages_for(user):
    count = inbox_count_for(user)
    unread_messages = [{'subject': p.thread.subject, 'sender': p.thread.latest_msg.sender.full_name(),'thread_id': p.thread.id, 'message_count':count} for p in
                           Participant.objects.inbox_for(user,read=False)[0:3]]#having the indexing on the Model object causes the ORM to issue a LIMIT sql query

    unread_messages.reverse()
    return unread_messages


def cached_inbox_messages_for(user):
    """
    The messages displayed in the navbar dropdown but cached if available
    :param user: a user object
    :return:messages: a json string with 'subject', 'sender', 'thread_id', and 'count' keys
    """
    messages = cache.get(INBOX_MESSAGE_CACHE % user.pk)
    if messages:
        return messages
    else:
        messages = inbox_messages_for(user)
        cache.set(INBOX_MESSAGE_CACHE % user.pk, dumps(messages), INBOX_MESSAGE_CACHE_TIME)
        return messages






