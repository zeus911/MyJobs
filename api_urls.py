from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

import api.views

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', api.views.api, name='api'),
    url(r'^countsapi.asp$', api.views.countsapi, name='counts_api'),
)
