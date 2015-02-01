from django.conf.urls import patterns, url

urlpatterns = patterns(
    'myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/partner$', 'filter_records',
        {'model': 'Partner',
         'output': 'myreports/includes/prm/partners.html'},
        name='filter_partners'),
    url(r'^ajax/contact$', 'filter_records',
        {'model': 'Contact',
         'output': 'myreports/includes/prm/contacts.html'},
        name='filter_contacts'),
    url(r'^ajax/(?P<model>\w+)$',
        'filter_records',
        {'output': 'json'},
        name='filter_records')
)
