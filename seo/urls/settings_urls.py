from django.conf.urls import patterns, url

from seo.views import settings_views

urlpatterns = patterns(
    '',

    # SeoSite
    url(r'^site/add',
        settings_views.SeoSiteSettingsFormView.as_view(),
        name='seosite_settings_add'),
    url(r'^site/delete/(?P<pk>\d+)/',
        settings_views.SeoSiteSettingsFormView.as_view(),
        name='seosite_settings_delete'),
    url(r'^site/update/(?P<pk>\d+)/',
        settings_views.SeoSiteSettingsFormView.as_view(),
        name='seosite_settings_update'),

    # SeoSites Domain
    url(r'^site/domain',
        settings_views.EmailDomainFormView.as_view(),
        name='seosites_settings_email_domain_edit')
)