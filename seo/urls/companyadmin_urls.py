from django.conf.urls import patterns, url


urlpatterns = patterns(
    'seo.views.companyadmin_views',
    url(r'settings$', 'site_settings', name='site_settings')
)