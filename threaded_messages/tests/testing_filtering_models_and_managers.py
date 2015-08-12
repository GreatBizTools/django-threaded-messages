from django.test import TestCase
from .models import Thread, Participant, Message, User
from .forms import ComposeForm


class SendingMessages(TestCase):

    def setUp(self):
        self.clerk = User.objects.get(id=4)
        self.verde = User.objects.get(id=1)

    def send_a_message(self):


