from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.forms import (CharField, ModelForm, ModelMultipleChoiceField,
                          Select, TextInput)

from mydashboard.models import SeoSite
from postajob.models import Job


class JobAdminForm(ModelForm):
    class Meta:
        model = Job

    apply_email = CharField(required=False, max_length=255,
                            widget=TextInput(attrs={'size': 50}))
    show_on_sites_widget = admin.widgets.FilteredSelectMultiple('Sites', False)
    show_on_sites = ModelMultipleChoiceField(SeoSite.objects.all(),
                                             required=False,
                                             widget=show_on_sites_widget)
    country = CharField(widget=Select(choices=Job.get_country_choices()),
                        initial='United States of America')
    state = CharField(widget=Select(choices=Job.get_state_choices()))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(JobAdminForm, self).__init__(*args, **kwargs)
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
        job = super(JobAdminForm, self).save(commit)

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


class JobAdmin(admin.ModelAdmin):
    exclude = ('guid', 'country_short', 'state_short', )
    form = JobAdminForm
    list_display = ('__unicode__', 'guid', )
    search_fields = ('title', 'company', 'show_on_sites__domain', )

    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'reqid', 'description', 'city', 'state',
                       'country', 'zipcode'),
        }),
        ('Application Instructions', {
            'fields': ('apply_link', 'apply_email', 'apply_info', ),
        }),
        ('Site Information', {
            'fields': ('company', 'show_on_sites', ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Override get_form() to allow the request information to be
        passed along to the JobAdminForm.

        """
        ModelForm = super(JobAdmin, self).get_form(request, obj, **kwargs)

        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass

    def delete_model(self, request, obj):
        obj.remove_from_solr()
        obj.delete()

admin.site.register(Job, JobAdmin)