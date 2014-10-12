from django.conf.urls import *

from myblocks import views


urlpatterns = patterns(
    '',
    url(r'^login/$', views.LoginView.as_view(), name="block"),
)
