from django.conf.urls import patterns, url
from myreports.views import ReportView

urlpatterns = patterns(
    'myreports.views',
    url(r'^view/overview$', 'overview', name='overview'),
    url(r'^view/archive$', 'report_archive', name='report_archive'),
    url(r'view/downloads$', 'downloads', name='downloads'),
    url(r'view/(?P<app>\w+)/(?P<model>\w+)$', ReportView.as_view(),
        name='reports'),
    url(r'^ajax/get-states', 'get_states', name='get_states'),
    url(r'^ajax/(?P<app>\w+)/(?P<model>\w+)$',
        'view_records',
        {'app': 'mypartners'},
        name='view_records'),
    url(r'download$', 'download_report', name='download_report'),
    url(r'ajax/get-inputs', 'get_inputs', name='get_inputs'),
)
