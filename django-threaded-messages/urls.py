from django.conf.urls import patterns, url, include
from django.contrib import admin

import ajax_select.urls as ajax_select_urls

urlpatterns = patterns('',
                       url(r'^admin/', admin.site.urls, ),
                       (r'^admin/lookups/', include(ajax_select_urls)),
                       url(r'^messages/',include('threaded_messages.urls', namespace='tm')),
                       )
