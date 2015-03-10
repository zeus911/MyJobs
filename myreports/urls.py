from django.conf.urls import patterns, url

urlpatterns = patterns(
    'myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/(?P<app>\w+)/(?P<model>\w+)$',
        'view_records',
        {'app': 'mypartners', 'output': 'json'},
        name='view_records'),
    url(r'^render$', 'create_report',
        {'app': 'mypartners', 'model': 'contactrecord'},
        name='create_report')
)
