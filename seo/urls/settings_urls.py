from django.conf.urls import patterns, url


urlpatterns = patterns(
    'seo.views.settings_views',
    url(r'site$', 'site_settings', name='site_settings')
)