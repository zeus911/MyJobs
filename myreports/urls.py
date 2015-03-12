from django.conf.urls import patterns, url

urlpatterns = patterns(
    'myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/get-states', 'get_states', name='get_states'),
    url(r'^ajax/(?P<app>\w+)/(?P<model>\w+)$',
        'filter_records',
        {'app': 'mypartners', 'output': 'json'},
        name='filter_records')
)
