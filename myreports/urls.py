from django.conf.urls import patterns, url

urlpatterns = patterns(
    'myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/partners$', 'search_records',
        {'model': 'Partner',
         'output': 'myreports/includes/prm/partners.html'},
        name='prm_filter_partners'),
    url(r'^ajax/contacts$', 'search_records',
        {'model': 'Contact',
         'output': 'myreports/includes/prm/contacts.html'},
        name='prm_filter_contacts'),
)

