from django.conf.urls import patterns, url

urlpatterns = patterns(
    'myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/get-states', 'get_states', name='get_states'),
    url(r'^ajax/get/(?P<app>\w+)/(?P<model>\w+)$',
        'view_records',
        {'app': 'mypartners', 'output': 'json'},
        name='view_records'),
    url(r'^ajax/render/(?P<app>\w+)/(?P<model>\w+)$',
        'create_report',
        {'app': 'mypartners'},
        name='create_report'),
    url(r'^download$', 'get_report', name='get_report'),
)
