from django.conf.urls import patterns, url, include
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^admin/', admin.site.urls, ),
                       url(r'^messages/',include('threaded_messages.urls', namespace='tm')),
                       )
