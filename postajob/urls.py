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
    url(r'^admin/$',
        views.products_overview,
        name='products_overview'),
    url(r'^admin/product/$',
        views.admin_products,
        name='product'),
    url(r'^admin/product/add/',
        views.ProductFormView.as_view(),
        name='product_add'),
    url(r'^admin/product/delete/(?P<pk>\d+)/',
        views.ProductFormView.as_view(),
        name='product_delete'),
    url(r'^admin/product/update/(?P<pk>\d+)/',
        views.ProductFormView.as_view(),
        name='product_update'),

    url(r'^admin/group/$',
        views.admin_groupings,
        name='productgrouping'),
    url(r'^admin/group/add/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_add'),
    url(r'^admin/group/delete/(?P<pk>\d+)/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_delete'),
    url(r'^admin/group/update/(?P<pk>\d+)/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_update'),

)
