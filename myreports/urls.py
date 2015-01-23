from django.conf.urls import patterns, url

urlpatterns = patterns('myreports.views',
    url(r'^view$', 'reports_overview', name='reports_overview'),
    url(r'^view/create-report$', 'create-report', name='create_report'),
)
