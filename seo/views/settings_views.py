from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View, RedirectView

from seo.forms import settings_forms
from seo.models import SeoSite
from universal.views import RequestFormViewBase


class SeoSiteSettingsFormView(RequestFormViewBase):
    display_name = 'Site'
    form_class = settings_forms.SeoSiteSettingsForm
    template_name = 'postajob/%s/form.html' % settings.PROJECT

    add_name = 'seosite_settings_add'
    update_name = 'seosite_settings_update'
    delete_name = 'seosite_settings_delete'

    def get_queryset(self, request):
        return SeoSite.objects.all()


class EmailDomainFormView(View):
    base_template_context = {
        'custom_action': 'Edit',
        'display_name': 'Email Domains'
    }
    template = 'postajob/%s/form.html' % settings.PROJECT

    def success_url(self):
        return reverse('purchasedmicrosite_admin_overview')

    def get(self, request):
        form = settings_forms.EmailDomainForm(request=request)
        kwargs = dict(self.base_template_context)
        kwargs.update({
            'form': form,
        })
        return render_to_response(self.template, kwargs,
                                  context_instance=RequestContext(request))

    def post(self, request):
        form = settings_forms.EmailDomainForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url())
        kwargs = dict(self.base_template_context)
        kwargs.update({
            'form': form,
        })
        return render_to_response(self.template, kwargs,
                                  context_instance=RequestContext(request))


def secure_redirect(request, page):
    """
    Redirects to the correct path on secure.my.jobs if this is not a network
    site, or 404 if it is.
    """
    if settings.SITE.site_tags.filter(site_tag='network').exists():
        return RedirectView.as_view(
            url='https://secure.my.jobs/%s' % page)(request)
    else:
        raise Http404
