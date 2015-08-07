from django.core.exceptions import PermissionDenied
from django.db.models import Q

from account.models import User
from tms.models import Classroom
from ajax_select import LookupChannel




class UserLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        if request.user.is_staff:
            try:
                query = int(q)
                result = list(Classroom.objects.filter(pk=query))
            except ValueError:
                result = list(User.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)))

            return result
        else:
            return list(User.objects.active_by_company(request.user.company).filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)))

    def format_match(self, obj):
        if isinstance(obj,Classroom):
            return "Class: {}".format(obj.id)
        else:
            if obj.last_name and obj.first_name:
                return "{},{}".format(obj.last_name, obj.first_name)
            else:
                return obj.username

    def format_item_display(self, obj):
        if isinstance(obj,Classroom):
            return "Class: {}".format(obj.id)
        else:
            if obj.last_name and obj.first_name:
                return "{},{}".format(obj.last_name, obj.first_name)
            else:
                return obj.username




    def check_auth(self,request):
        if not request.user.is_authenticated():
            raise PermissionDenied

AJAX_LOOKUP_CHANNELS = {
    'all' : ('azul_messaging.lookup', 'UserLookup'),

}