from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.forms import (CharField, CheckboxSelectMultiple, ModelForm,
                          ModelMultipleChoiceField, Select, TextInput)

from mydashboard.models import SeoSite
from mypartners.widgets import SplitDateDropDownField
from postajob.models import Job


class JobForm(ModelForm):
    class Meta:
        exclude = ('guid', 'country_short', 'state_short', 'is_syndicated', )
        fields = ('title', 'is_syndicated', 'reqid', 'description', 'city',
                  'state', 'country', 'zipcode', 'date_expired', 'is_expired',
                  'autorenew', 'apply_link', 'apply_email', 'apply_info',
                  'company', 'show_on_sites', )
        model = Job

    apply_email = CharField(required=False, max_length=255,
                            label='Apply Email',
                            widget=TextInput(attrs={'size': 50}))
    apply_link = CharField(required=False, max_length=255,
                           label='Apply Link',
                           widget=TextInput(attrs={'rows': 1, 'size': 50}))
    show_on_sites_widget = admin.widgets.FilteredSelectMultiple('Sites', False)
    show_on_sites = ModelMultipleChoiceField(SeoSite.objects.all(),
                                             label="On Sites",
                                             required=False,
                                             widget=show_on_sites_widget)
    country = CharField(widget=Select(choices=Job.get_country_choices()),
                        initial='United States of America')
    state = CharField(widget=Select(choices=Job.get_state_choices()))
    date_expired = SplitDateDropDownField(label="Expires On")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(JobForm, self).__init__(*args, **kwargs)
        if not self.request.path.startswith('/admin'):
            # Prevent all three apply options from being show on the page at
            # once.
            apply_choices = [('link', "Link"), ('email', 'Email'),
                             ('instructions', 'Instructions')]
            if self.instance and self.instance.apply_info:
                apply_initial = 'instructions'
            else:
                apply_initial = 'link'
            self.fields['apply_type'] = CharField(label='Application Method',
                                                  widget=Select(choices=apply_choices),
                                                  initial=apply_initial)

            # Place the apply_choices filter in a place that makes sense.
            self.fields.keyOrder.pop(-1)
            apply_link_index = self.fields.keyOrder.index('apply_link')
            self.fields.keyOrder.insert(apply_link_index, 'apply_type')

            # FilteredSelectMultiple doesn't work outside the admin, so
            # switch to a widget that does work.
            self.fields['show_on_sites'].widget = CheckboxSelectMultiple(
                attrs={'class': 'job-sites-checkbox'})
            # After changing the widget the queryset also needs reset.
            self.fields['show_on_sites'].queryset = SeoSite.objects.all()

        if not self.request.user.is_superuser:
            # Limit a user's access to only companies/sites they own.
            kwargs = {'admins': self.request.user}
            self.fields['company'].queryset = \
                self.fields['company'].queryset.filter(**kwargs)
            kwargs = {'business_units__company__admins': self.request.user}
            self.fields['show_on_sites'].queryset = \
                self.fields['show_on_sites'].queryset.filter(**kwargs).distinct()

    def clean_apply_link(self):
        """
        If the apply_link is a url and not a mailto, format the link
        appropriately and confirm it really is a url.

        """
        apply_link = self.cleaned_data.get('apply_link')
        if apply_link and apply_link.startswith('mailto:'):
            return apply_link
        if apply_link and not (apply_link.startswith('http://') or
                               apply_link.startswith('https://')):
            apply_link = 'http://{link}'.format(link=apply_link)
        if apply_link:
            URLValidator(apply_link)
        return apply_link

    def clean(self):
        apply_info = self.cleaned_data.get('apply_info')
        apply_link = self.cleaned_data.get('apply_link')
        apply_email = self.cleaned_data.get('apply_email')

        # Require one set of apply instructions.
        if not apply_info and not apply_link and not apply_email:
            raise ValidationError('You must supply some type of appliction '
                                  'information.')
        # Allow only one set of apply instructions.
        if sum([1 for x in [apply_info, apply_link, apply_email] if x]) > 1:
            raise ValidationError('You can only supply one application '
                                  'method.')

        if apply_email:
            # validate_email() raises its own ValidationError.
            validate_email(apply_email)
            # If the apply instructions are an email, it needs to be
            # reformatted as a mailto and saved as the link.
            apply_email = 'mailto:{link}'.format(link=apply_email)
            self.cleaned_data['apply_link'] = apply_email

        return self.cleaned_data

    def save(self, commit=True):
        sites = self.cleaned_data['show_on_sites']
        job = super(JobForm, self).save(commit)

        country = job.country
        state = job.state
        try:
            job.state_short = Job.get_state_map()[state]
        except IndexError:
            job.state_short = None
        try:
            job.country_short = Job.get_country_map()[country]
        except IndexError:
            job.country_short = None

        # The object must have a primary key before the many-to-many
        # relationship can be created.
        if not job.pk:
            job.save()
        [job.show_on_sites.add(s) for s in sites]
        return job