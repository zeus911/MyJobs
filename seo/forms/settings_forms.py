from django import forms

from seo.models import SeoSite
from universal.forms import RequestForm
from universal.helpers import get_company_or_404


class SeoSiteSettingsForm(RequestForm):
    class Meta:
        model = SeoSite


class EmailDomainForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        company = get_company_or_404(request)
        sites = SeoSite.objects.filter(canonical_company=company)
        super(EmailDomainForm, self).__init__(*args, **kwargs)
        email_domain_field = SeoSite._meta.get_field('email_domain')
        for site in sites:
            print site.email_domain_choices()
            field_kwargs = {
                'widget': forms.Select(),
                'choices': site.email_domain_choices(),
                'initial': email_domain_field.get_default(),
                'label': 'Email Domain For %s' % site.domain,
            }
            self.fields[str(site.pk)] = forms.ChoiceField(**field_kwargs)