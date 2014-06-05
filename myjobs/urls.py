from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

from myjobs.views import *

accountpatterns = patterns('MyJobs.myjobs.views',
    url(r'^edit/$', 'edit_account', name='edit_account'),
    url(r'^delete$', 'delete_account', name='delete_account'),
    url(r'^disable$', 'disable_account', name='disable_account'),
    url(r'^$',
        RedirectView.as_view(url='/account/edit/')),
)

urlpatterns = patterns('MyJobs.myjobs.views',
    url(r'^$', 'home', name='home'),
    url(r'^about/$', About.as_view(), name='about'),
    url(r'^about/testimonials/$', Testimonials.as_view(), name='testimonials'),
    url(r'^privacy/$', Privacy.as_view(), name='privacy'),
    url(r'^terms/$', Terms.as_view(), name='terms'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^contact-faq', 'contact_faq', name='contact_faq'),
    url(r'^batch$', 'batch_message_digest', name='batch_message_digest'),
    url(r'^unsubscribe/$', unsubscribe_all, name='unsubscribe_all'),
    url(r'^account/', include(accountpatterns)),
    url(r'^send/$', 'continue_sending_mail', name='continue_sending_mail'),
    url(r'^toolbar/$', 'toolbar', name='toolbar'),
    url(r'^cas/$', 'cas', name='cas'),
    url(r'^topbar/$', 'topbar', name='topbar'),
)
