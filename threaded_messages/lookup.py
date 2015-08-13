from django.core.exceptions import PermissionDenied
from django.db.models import Q

from account.models import User
from tms.models import Classroom, Trainee
from ajax_select import LookupChannel




class UserLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        if request.user.user_type=='admin':
            try:
                query = int(q)
                result = Classroom.objects.filter(trainers=request.user).filter(pk=query)
                for r in result:
                    r.id = "class_{}".format(r.id)
            except ValueError:
                result = list(User.objects.active_by_company(request.user.company).filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)))
                for r in result:
                    r.id = "user_{}".format(r.id)
            return result
        else:
            trainees_classroom = Trainee.objects.get(user=request.user).classroom
            trainers = trainees_classroom.trainers.all()
            trainees = Trainee.objects.filter(classroom=trainees_classroom)
            trainees = [t.user for t in trainees]
            result = list(trainees) + list(trainers)
            for r in result:
                r.id = "user_{}".format(r.id)
            return result



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
            return "Class: {}".format(obj.id.split("_")[1])
        else:
            if obj.last_name and obj.first_name:
                return "{},{}".format(obj.last_name, obj.first_name)
            else:
                return obj.username


    def check_auth(self,request):
        if not request.user.is_authenticated():
            raise PermissionDenied

AJAX_LOOKUP_CHANNELS = {
    'all' : ('threaded_messages.lookup', 'UserLookup'),

}