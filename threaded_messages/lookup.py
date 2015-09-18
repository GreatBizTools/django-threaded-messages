from django.contrib.auth.models import User
from django.db.models import Q


from ajax_select import LookupChannel




class UserLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return User.objects.filter(Q(username__icontains = q) | Q(first_name__icontains = q) | Q(last_name__icontains = q))

AJAX_LOOKUP_CHANNELS = {
    'all' : ('threaded_messages.lookup', 'UserLookup'),

}