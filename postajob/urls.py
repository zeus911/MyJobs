from django.conf.urls import *

from postajob import views

urlpatterns = patterns(
    '',
    url(r'^add', views.JobFormView.as_view(), name='job_add'),
    url(r'^delete/(?P<pk>\d+)', views.JobFormView.as_view(), name='job_delete'),
    url(r'^update/(?P<pk>\d+)', views.JobFormView.as_view(), name='job_update'),
    url(r'^$', views.jobs_overview, name='jobs_overview'),
)
