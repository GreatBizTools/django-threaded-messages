from django.conf.urls import *
from django.views.generic import RedirectView

from threaded_messages.views import *

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='inbox/')),
    url(r'^search/$', search, name='messages_search'),
    url(r'^inbox/$', inbox, name='messages_inbox'),
    url(r'^outbox/$', outbox, name='messages_outbox'),
    url(r'^compose/$', compose, name='messages_compose'),
    url(r'^compose/(?P<recipient>[\w.+-_]+)/$', compose, name='messages_compose_to'),
    url(r'^view/(?P<thread_id>[\d]+)/$', view, name='messages_detail'),
    url(r'^delete/(?P<thread_id>[\d]+)/$', delete, name='messages_delete'),
    url(r'^undelete/(?P<thread_id>[\d]+)/$', undelete, name='messages_undelete'),
    url(r'^batch-update/$', batch_update, name='messages_batch_update'),
    url(r'^trash/$', trash, name='messages_trash'),
    url(r'^update-navbar/$', update_navbarView, name='messages_update'),
    url(r"^recipient-search/$", recipient_search, name="recipient_search"),
    url(r'^message-reply/(?P<thread_id>[\d]+)/$', message_ajax_reply, name="message_reply"),
)
