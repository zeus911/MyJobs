from django.conf.urls import patterns, url

from myemails.views import (Overview, ViewTemplate, IframeView, EditTemplate,
                            ManageHeaderFooter, manage_template)

urlpatterns = patterns(
    'myemails.views',
    url(r'^get-fields/$', 'get_fields', name='get_fields'),
    url(r'view/$', Overview.as_view(), name='email-overview'),
    url(r'view/manage/view$', ManageHeaderFooter.as_view(), name='manage-h-f'),
    url(r'view/template/manage$', manage_template, name='manage-template'),
    url(r'view/template/edit$', EditTemplate.as_view(), name='edit-template'),
    url(r'view/template/view$', ViewTemplate.as_view(), name='view-template'),
    url(r'view/template/iframe$', IframeView.as_view(), name='iframe-view'),
)
