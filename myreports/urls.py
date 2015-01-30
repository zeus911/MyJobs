from django.conf.urls import patterns, url

urlpatterns = patterns('myreports.views',
    url(r'^view$', 'reports', name='reports'),
    url(r'^ajax/partners$', 'prm_filter_partners', name='prm_filter_partners'),
    url(r'^ajax/contacts$', 'prm_filter_contacts', name='prm_filter_contacts'),
    url(r'^search$', 'search_records', name='search_records')
)
