from django.test import TestCase
from .models import Thread, Participant, Message, User
from .forms import ComposeForm


class SendingMessages(TestCase):

    def setUp(self):
        self.mortimer = User.objects.create_user('mort', 'mort@gmail.com', 'password')
        self.harry = User.objects.create_user('harry','harry@gmail.com', 'password')
        user_id = "user_{}".format(self.mortimer.id)
        self.form = ComposeForm(subject="This is a message!", body="Yes, absolutely.", recipients=[user_id])
        self.form.save(self.harry)
        self.thread = Thread.objects.get(id=1)
        self.message = self.thread.latest_msg

    def test_thread_recipients(self):
        """
        A sent message will result in a thread of which both sender and recipient are participants.
        """
        self.participants = Participant.objects.filter(thread=self.thread)
        self.assertIn(self.mortimer, self.participants, "Recipient is a participant")
        self.assertIn(self.harry, self.participants, "Sender is a participant")

    def test_message_sender(self):
        self.sender = self.message.sender
        self.assertEqual(self.sender, self.harry)

