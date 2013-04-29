from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('', include('MyJobs.myjobs.urls')),
    url('', include('django_messages.urls')),
    url(r'^accounts/', include('MyJobs.registration.urls')),
    url(r'^profile/', include('MyJobs.myprofile.urls')),
    url(r'^saved-search/', include('MyJobs.mysearches.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
