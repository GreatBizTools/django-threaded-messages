from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.test.utils import override_settings

import haystack
from urlparse import urlparse
import os


from threaded_messages.models import Thread, Participant, Message, User
from threaded_messages.forms import ComposeForm, ReplyForm
from threaded_messages.utils import now



class SendingMessages(TestCase):

    def setUp(self):
        self.mortimer = User.objects.create_user('mort', 'mort@gmail.com', 'password')
        self.harry = User.objects.create_user('harry','harry@gmail.com', 'password')
        user_id = "user_{}".format(self.mortimer.id)
        self.form = ComposeForm(data={'subject':"This is a message!", 'body':"Yes, absolutely.", 'recipient':user_id})
        print self.form.is_valid()
        self.form.save(self.harry)
        self.thread = Thread.objects.get(subject="This is a message!")
        self.message = self.thread.latest_msg

    def test_thread_recipients(self):
        """
        A sent message will result in a thread of which both sender and recipient are participants.
        """
        participants = Participant.objects.filter(thread=self.thread)
        participants = [p.user for p in participants]
        self.assertIn(self.mortimer, participants, "Recipient is a participant")
        self.assertIn(self.harry, participants, "Sender is a participant")

    def test_message_sender(self):
        """
        The latest message is sent by the message sender
        """
        sender = self.message.sender
        self.assertEqual(sender, self.harry)


    def test_archived_time(self):
        """
        Test that when the user archives a thread, it is assigned a deleted_at date
        Used in views.py:batch_update
        """
        time_of_archive = now()
        participant = self.thread.participants.get(user=self.mortimer)
        participant.deleted_at = time_of_archive
        participant.save()
        participant_from_database = self.thread.participants.get(user=self.mortimer)
        self.assertEqual(participant_from_database.deleted_at, time_of_archive, "The archived date is correctly set")


    def test_read_at_time(self):
        """
        Test that when the user reads a thread, it is assigned a read_at date
        using the read_thread method on Participant object
        """
        participant = self.thread.participants.get(user=self.mortimer)
        participant.read_thread()
        self.assertTrue(participant.read_at is not None, "There is a read_at date. Message was read")


    def test_reply_creates_new_message(self):
        """
        Test that when a user replies to a thread a new message is made in the Thread object
        """
        form = ReplyForm({'body':'This is the message body'})
        self.assertTrue(form.is_valid(), "The form is valid.")
        form.save(sender=self.mortimer, thread=self.thread)
        messages = self.thread.all_msgs.all()
        self.assertTrue(len(messages)==2, "A replied message creates a second message.")


class TestingInboxAndOutboxViews(TestCase):
    """Tests the inbox and outbox views in the views.py file"""
    def setUp(self):
        self.client = Client()
        self.mortimer = User.objects.create_user('mort', 'mort@gmail.com', 'password')
        self.harry = User.objects.create_user('harry','harry@gmail.com', 'password')
        user_id = "user_{}".format(self.mortimer.id)
        self.form = ComposeForm(data={'subject':"This is a message!", 'body':"Yes, absolutely.", 'recipient':user_id})
        print self.form.is_valid()
        self.form.save(self.harry)
        self.thread = Thread.objects.get(subject="This is a message!")
        self.message = self.thread.latest_msg

    def test_inbox_view_thread_list_count(self):
        """
        Tests that the inbox response has context 'thread_list' with the correct length (Number of messages)
        """
        self.client.login(username='mort', password='password')
        response = self.client.get(reverse('tm:messages_inbox'))
        self.assertEqual(response.status_code, 200, "Recipient has logged in successfully")
        thread_list = response.context['thread_list']
        self.assertTrue(len(thread_list)==1,"There is one message in the recipeint's thread_list")

    def test_inbox_view_thread_list_count_for_sender(self):
        """
        Tests that the sender has a message in their inbox
        """
        self.client.login(username=self.harry.username, password='password')
        response = self.client.get(reverse('tm:messages_inbox'))
        self.assertEqual(response.status_code, 200, "Sender has logged in successfully")
        thread_list = response.context['thread_list']
        self.assertTrue(len(thread_list)==1, "There is one message in the sender's thread_list")

    def test_inbox_view_read_thread_list_count_for_sender(self):
        """
        Tests that the thread has been read for the sender and so there should be no unread messages in inbox
        """
        self.client.login(username=self.harry.username, password='password')
        response = self.client.get(reverse('tm:messages_inbox'),{'only_unread':1})
        self.assertEqual(response.status_code, 200, "Sender has logged in successfully")
        thread_list = response.context['thread_list']
        self.assertTrue(len(thread_list)==0, "There are no unread messages in the sender's inbox")

    def test_inbox_view_unread_thread_list_count_for_recipient(self):
        """
        Tests that the recipient has an unread message in inbox's thread_list context
        """
        self.client.login(username=self.mortimer.username, password='password')
        response = self.client.get(reverse('tm:messages_inbox'),{'only_unread':1})
        self.assertEqual(response.status_code, 200, "Recipient has logged in successfully")
        thread_list = response.context['thread_list']
        self.assertTrue(len(thread_list)==1, "There is one unread message in the recipient's inbox")

    def test_outbox_view_thread_list_for_sender(self):
        """
        Tests that the sender has a sent message in outbox
        """
        self.client.login(username=self.harry.username, password='password')
        response = self.client.get(reverse('tm:messages_outbox'))
        self.assertEqual(response.status_code, 200, "Sender has logged in successfully")
        thread_list = response.context['thread_list']
        self.assertTrue(len(thread_list)==1, "There is a message in sender's outbox")

    def test_outbox_view_thread_list_for_recipient(self):
        """
        Tests that the recipient doesn't have a message in outbox
        """
        self.client.login(username=self.mortimer.username, password='password')
        response = self.client.get(reverse('tm:messages_outbox'))
        self.assertEqual(response.status_code, 200, "Recipient has logged in successfully")
        thread_list = response.context['thread_list']
        self.assertTrue(len(thread_list)==0,"There are no messages in the recipient's outbox")




es = urlparse(os.environ.get('BONSAI_URL', 'http://127.0.0.1:9200/'))
if es.port:
    port = es.port
else:
    port = {
        'https': 443,
        'http': 80
    }.get(es.scheme, es.port or 80)

TEST_INDEX = {
    'default': {
        'ENGINE': 'azul_search.backends.PatchedElasticsearchSearchEngine',
        'URL': es.scheme + '://' + es.hostname + ':' + str(port),
        'INDEX_NAME': 'test_index',
        'INCLUDE_SPELLING': True,
    },
}

@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class SearchTest(TestCase):
    """Tests the search view"""
    def setUp(self):
        haystack.connections.reload('default')
        super(SearchTest, self).setUp()

        self.mortimer = User.objects.create_user('mort', 'mort@gmail.com', 'password')
        self.harry = User.objects.create_user('harry','harry@gmail.com', 'password')
        user_id = "user_{}".format(self.mortimer.id)
        self.form = ComposeForm(data={'subject':"This is a message!", 'body':"Yes, absolutely.", 'recipient':user_id})
        print self.form.is_valid()
        self.form.save(self.harry)

        form2 = ComposeForm(data={'subject':'This is not a message!', 'body':'Yeah, right.', 'recipient':"user_{}".format(self.harry.id)})
        print form2.is_valid()
        form2.save(self.mortimer)

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)


    def test_search_for_word_in_both(self):
        """
        Tests for a word in both messages
        """
        self.client.login(username=self.harry.username, password='password')
        response = self.client.get(reverse('tm:messages_search'),{'qs': 'message'})
        self.assertEqual(response.status_code, 200, "User successfully logged in.")
        thread_results = response.context['thread_results']
        self.assertEqual(len(thread_results),2,"The word was in both messages.")

    def test_search_for_word_in_only_one(self):
        """
        Tests for a word in one message but not the other
        """
        # TODO: Fix functionality. Searching for differing word in body works, but in subject doesn't
        self.client.login(username=self.harry.username, password='password')
        response = self.client.get(reverse('tm:messages_search'),{'qs': 'absolutely'})
        self.assertEqual(response.status_code, 200, "User successfully logged in.")
        thread_results = response.context['thread_results']
        self.assertEqual(len(thread_results), 1, "The word was in just one message.")

    def test_for_empty_archives(self):
        """
        Tests that when no messages are archived the search will not return any
        """
        self.client.login(username=self.harry.username, password='password')
        response = self.client.get(reverse('tm:messages_search'),{'qs': 'message', 'search': 'archives'})
        self.assertEqual(response.status_code, 200, "User successfully logged in.")
        thread_results = response.context['thread_results']
        self.assertEqual(len(thread_results), 0, "There are no messages in archives.")

    def test_archives_after_archiving_individual_thread(self):
        """
        Tests that after archiving a single message it shows up in the archive search
        """
        self.client.login(username=self.harry.username, password='password')
        thread = Thread.objects.get(subject__icontains='not')
        response_from_archive = self.client.get(reverse('tm:messages_delete', args=[thread.id]))
        self.assertEqual(response_from_archive.status_code, 302, "Successfully archived thread") #it's a response redirect
        response = self.client.get(reverse('tm:messages_search'),{'qs': 'message', 'search': 'archives'})
        self.assertEqual(response.status_code, 200, "User successfully logged in.")
        thread_results = response.context['thread_results']
        self.assertEqual(len(thread_results), 1, "There is one message in the archives.")

    def test_archives_after_bulk_archive_of_thread(self):
        """
        Tests that after bulk archiving, using the batch_update method in the views, the thread will be
        searchable in the archives.
        """
        self.client.login(username=self.harry.username, password='password')
        thread = Thread.objects.get(subject__icontains='not')
        response_from_archive = self.client.post(reverse('tm:messages_batch_update'),data={'batchupdateids': [thread.id], 'action': 'delete'})
        self.assertEqual(response_from_archive.status_code, 302, "Successfully archived thread")#it's a response redirect
        response = self.client.get(reverse('tm:messages_search'),{'qs': 'message', 'search': 'archives'})
        self.assertEqual(response.status_code, 200, "User successfully logged in.")
        thread_results = response.context['thread_results']
        self.assertEqual(len(thread_results), 1, "There is one message in the archives.")
