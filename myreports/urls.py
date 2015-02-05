from django.conf.urls import patterns, url

urlpatterns = patterns(
    'myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/partner$', 'filter_records',
        {'app': 'mypartners', 'model': 'partner',
         'output': 'myreports/includes/prm/partners.html'},
        name='filter_partners'),
    url(r'^ajax/contact$', 'filter_records',
        {'app': 'mypartners', 'model': 'contact',
         'output': 'myreports/includes/prm/contacts.html'},
        name='filter_contacts'),
    url(r'^ajax/(?P<app>\w+)/(?P<model>\w+)$',
        'filter_records',
        {'app': 'mypartners', 'output': 'json'},
        name='filter_records')
)
