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
    url('', include('MyJobs.myjobs.urls')),
    url(r'^candidates/', include('MyJobs.mydashboard.urls')),
    url(r'^accounts/', include('MyJobs.registration.urls')),
    url(r'^profile/', include('MyJobs.myprofile.urls')),
    url(r'^saved-search/', include('MyJobs.mysearches.urls')),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authorize/', include('MyJobs.mysignon.urls')),
    url(r'^message/', include('MyJobs.mymessages.urls')),
    url(r'^prm/', include('MyJobs.mypartners.urls')),
    url(r'^postajob/', include('MyJobs.postajob.urls')),
)


if repr(getattr(default_storage, 'connection', '')) != 'S3Connection:s3.amazonaws':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
