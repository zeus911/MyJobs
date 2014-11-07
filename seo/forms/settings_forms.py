from django import forms

from seo.models import SeoSite
from universal.forms import RequestForm


class SeoSiteSettingsForm(RequestForm):
    class Meta:
        model = SeoSite


class EmailDomainForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs['request']
        super(EmailDomainForm, self).__init__(*args, **kwargs)
