from django.conf.urls import patterns, url


urlpatterns = patterns('mymessages.views',
    url(r'^$', 'read', name='read'),
)
