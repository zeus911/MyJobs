from django.conf.urls import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns('MyJobs.mypartners.views',
    url(r'^$', RedirectView.as_view(url='/partners/view/')),
    url(r'^view/$', 'prm', name='prm'),
    url(r'^view$', 'prm', name='prm'),
    url(r'^view/details$', 'partner_details', name='partner_details'),
    url(r'^view/save$', 'save_init_partner_form', name='save_init_partner_form'),
    url(r'^view/edit$', 'edit_item', name='edit_partner'),
    url(r'^view/details/edit$', 'edit_item', name='edit_contact'),
    url(r'^view/details/save$', 'save_item', name='save_item'),
)