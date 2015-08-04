from threaded_messages.models import cached_inbox_count_for


def inbox(request):
    if request.user.is_authenticated():
        return {'messages_inbox_count': cached_inbox_count_for(request.user)}
    else:
        return {}
