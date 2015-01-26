from django.conf.urls import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import default_storage

from tastypie.api import Api

from myjobs.api import UserResource, SavedSearchResource
from seo.views.search_views import BusinessUnitAdminFilter, SeoSiteAdminFilter

admin.autodiscover()

# API Resources
v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(SavedSearchResource())

handler500 = "myjobs.views.error_500"


urlpatterns = patterns(
    '',
    url('', include('myjobs.urls')),
    url(r'^candidates/', include('mydashboard.urls')),
    url(r'^profile/', include('myprofile.urls')),
    url(r'^saved-search/', include('mysearches.urls')),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authorize/', include('mysignon.urls')),
    url(r'^message/', include('mymessages.urls')),
    url(r'^prm/', include('mypartners.urls')),
    url(r'^posting/', include('postajob.urls')),
    url(r'^reports/', include('myreports.urls')),
)


urlpatterns += patterns(
    '',
    url(r'^accounts/', include('registration.urls')),
)

# Filtering URLs
urlpatterns += patterns(
    '',
    url(r'^ajax/data/filter/business_units/$',
        BusinessUnitAdminFilter.as_view(),
        name='buid_admin_fsm'),
    url(r'^data/filter/sites/$', SeoSiteAdminFilter.as_view(),
        name='site_admin_fsm')
)

if repr(getattr(default_storage, 'connection', '')) != 'S3Connection:s3.amazonaws.com':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
