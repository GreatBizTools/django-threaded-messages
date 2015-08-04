from django.contrib import admin
from threaded_messages.models import *


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'sent_at', 'body')
    ordering = ('-sent_at',)
    search_fields = ('body', 'sender__first_name',
                     'sender__last_name', 'sender__username')
    raw_id_fields = ('sender', 'parent_msg')
    readonly_fields = ('subject',)

    def subject(self, msg):
        return msg.thread.all()[0].subject
admin.site.register(Message, MessageAdmin)


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'creator', 'replied')
    search_fields = ('subject', 'creator__first_name',
                     'creator__last_name', 'creator__username')
admin.site.register(Thread, ThreadAdmin)


admin.site.register(Participant)
