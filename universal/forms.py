from django.forms import ModelForm

from universal.helpers import get_company


class RequestForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.company = get_company(self.request)
        super(RequestForm, self).__init__(*args, **kwargs)


class NormalizedModelForm(ModelForm):

    def clean(self):
        self.cleaned_data = {key: ' '.join(value.split())
                             for key, value in self.cleaned_data.items()}
        return super(NormalizedModelForm, self).clean()
