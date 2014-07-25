from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from registration.forms import CustomPasswordResetForm
from registration.views import (RegistrationComplete, activate, merge_accounts,
                                resend_activation, logout,
                                password_reset_with_activation)

urlpatterns = patterns('',
    # Authorization URLS

    url(r'^password/reset/$', password_reset_with_activation,
        {'password_reset_form': CustomPasswordResetForm},
        name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.password_reset_done,
        name='password_reset_done'),

    #Registration URLS
    url(r'^register/complete/$',
        RegistrationComplete.as_view(), name='register_complete'),
    url(r'^activate/(?P<activation_key>(\S+))/$', activate,
        name='registration_activate'),
    url(r'^merge/(?P<activation_key>(\S+))/$', merge_accounts,
        name='merge_accounts'),
    url(r'^register/resend/$', resend_activation, name='resend_activation'),
    url(r'^logout/$', logout, name='auth_logout'),
)
