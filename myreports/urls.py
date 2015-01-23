from django.conf.urls import patterns, url

urlpatterns = patterns('myreports.views',
    url(r'^view$', 'reports', name='reports'),
)
