from django.core.exceptions import PermissionDenied
from django.db.models import Q

from account.models import User
from tms.models import Classroom, Trainee
from ajax_select import LookupChannel




class UserLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        if request.user.is_staff:
            try:
                query = int(q)
                result = Classroom.objects.filter(pk=query)
                for r in result:
                    r.id = "class_{}".format(r.id)
            except ValueError:
                result = list(User.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)))
                for r in result:
                    r.id = "user_{}".format(r.id)
            return result
        else:
            return list(User.objects.active_by_company(request.user.company).filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)))

    def format_match(self, obj):
        if isinstance(obj,Classroom):
            return "Class: {}".format(obj.id.split("_")[1])
        else:
            if obj.last_name and obj.first_name:
                return "{},{}".format(obj.last_name, obj.first_name)
            else:
                return obj.username

    def format_item_display(self, obj):
        if isinstance(obj, Classroom):
            names=[]
            trainee_List = Trainee.objects.filter(classroom_id=int(obj.id.split("_")[1]))
            for trainee in trainee_List:
                if trainee.user.last_name and trainee.user.first_name:
                    names.append("{},{}".format(trainee.user.last_name, trainee.user.first_name))
                else:
                    names.append(trainee.user.username)
            return "  ".join(names)
        else:
            if obj.last_name and obj.first_name:
                return "{},{}".format(obj.last_name, obj.first_name)
            else:
                return obj.username

    def get_objects(self, ids):
        objects = []
        for id in ids:
            id_list = id.split("_")
            print type(id_list[0])
            if u"user"==id_list[0]:
                print "We've got a user!"
                objects.append(User.objects.get(pk=id_list[1]))
            else:
                print "We don't have a user?"
                trainee_objects = Trainee.objects.filter(classroom_pk=id_list[1])
                objects.append([t.user for t in trainee_objects])
        return objects

    def check_auth(self,request):
        if not request.user.is_authenticated():
            raise PermissionDenied

AJAX_LOOKUP_CHANNELS = {
    'all' : ('threaded_messages.lookup', 'UserLookup'),

}