from django.conf.urls import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import default_storage

from tastypie.api import Api

from myjobs.api import UserResource, SavedSearchResource

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
    url(r'^accounts/', include('registration.urls')),
    url(r'^profile/', include('myprofile.urls')),
    url(r'^saved-search/', include('mysearches.urls')),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authorize/', include('mysignon.urls')),
    url(r'^message/', include('mymessages.urls')),
    url(r'^prm/', include('mypartners.urls')),
    url(r'^postajob/', include('postajob.urls')),
)


if repr(getattr(default_storage, 'connection', '')) != 'S3Connection:s3.amazonaws.com':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
