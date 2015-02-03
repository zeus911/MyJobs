from django.conf.urls import patterns, url


urlpatterns = patterns('mymessages.views',
    url(r'^$', 'read', name='read'),
    url(r'^delete/$', 'delete', name='delete'),
    url(r'^inbox/$', 'inbox', name='inbox'),
)
