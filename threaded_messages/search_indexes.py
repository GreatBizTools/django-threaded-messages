from haystack import indexes
from .models import Thread


class ThreadIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    participants = indexes.MultiValueField()
    participant_last_names = indexes.MultiValueField()
    participant_archived = indexes.MultiValueField()
    participant_sent = indexes.MultiValueField()
    last_message = indexes.DateTimeField(model_attr='latest_msg__sent_at')

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_participants(self, object):
        return [p.user.pk for p in object.participants.all()]

    def prepare_participant_last_names(self, object):
        return [p.user.last_name for p in object.participants.all()]

    def prepare_participant_archived(self, object):
        return ["{}-{}".format(p.user.pk,p.deleted_at is not None) for p in object.participants.all()]

    def prepare_participant_sent(self, object):
        return ["{}-{}".format(p.user.pk, p.replied_at is not None) for p in object.participants.all()]

    def get_model(self):
        return Thread
