from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views

from registration.forms import CustomSetPasswordForm
from registration.views import (RegistrationComplete, activate, merge_accounts,
                                resend_activation, logout,
                                custom_password_reset)


urlpatterns = patterns('',
    # Authorization URLS
    url(r'^password/reset/$', custom_password_reset,
        name='password_reset'),

    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {
            'template_name': "registration/%s/password_reset_confirm.html" % settings.PROJECT,
            'set_password_form': CustomSetPasswordForm
        },
        name='password_reset_confirm'),

    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
        {
            'template_name': "registration/%s/password_reset_complete.html" % settings.PROJECT,
        },
        name='password_reset_complete'),

    url(r'^password/reset/done/$', auth_views.password_reset_done,
        {
            'template_name': "registration/%s/password_reset_done.html" % settings.PROJECT,
        },
        name='password_reset_done'),

    #Registration URLS
    url(r'^register/complete/$',
        RegistrationComplete.as_view(), name='register_complete'),
    url(r'^activate/(?P<activation_key>(\S+))/$', activate,
        name='registration_activate'),

    url(r'^invitations/(?P<activation_key>(\S+))/$', activate,
        {'invitation': True},
        name='invitation_activate'),

    url(r'^merge/(?P<activation_key>(\S+))/$', merge_accounts,
        name='merge_accounts'),

    url(r'^register/resend/$', resend_activation, name='resend_activation'),

    url(r'^logout/$', logout, name='auth_logout'),
)
