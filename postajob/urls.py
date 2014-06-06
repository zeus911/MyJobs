from django.conf.urls import *

from postajob import views

urlpatterns = patterns(
    '',

    # Posted job management for members
    url(r'^job/add/',
        views.JobFormView.as_view(),
        name='job_add'),
    url(r'^job/delete/(?P<pk>\d+)/',
        views.JobFormView.as_view(),
        name='job_delete'),
    url(r'^job/update/(?P<pk>\d+)/',
        views.JobFormView.as_view(),
        name='job_update'),
    url(r'^jobs/$',
        views.jobs_overview,
        name='jobs_overview'),

    # Product management
    url(r'^product/add/',
        views.ProductFormView.as_view(),
        name='product_add'),
    url(r'^product/delete/(?P<pk>\d+)/',
        views.ProductFormView.as_view(),
        name='product_delete'),
    url(r'^product/update/(?P<pk>\d+)/',
        views.ProductFormView.as_view(),
        name='product_update'),
    url(r'^products/$',
        views.products_overview,
        name='products_overview'),

    url(r'^product/group/add/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_add'),
    url(r'^product/group/delete/(?P<pk>\d+)/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_delete'),
    url(r'^product/group/update/(?P<pk>\d+)/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_update'),

)
