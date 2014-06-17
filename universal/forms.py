from django.forms import ModelForm

from universal.helpers import get_company


class RequestForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.company = get_company(self.request)
        super(RequestForm, self).__init__(*args, **kwargs)