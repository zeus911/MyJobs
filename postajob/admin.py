from django.contrib import admin
from django.forms import (CharField, ModelForm, ModelMultipleChoiceField,
                          Select)

from mydashboard.models import SeoSite
from postajob.models import Job


class JobAdminForm(ModelForm):
    class Meta:
        model = Job

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
            self.fields['company'].queryset = self.fields['company'].queryset.filter(admins=self.request.user)
            self.fields['show_on_sites'].queryset = self.fields['show_on_sites'].queryset.filter(business_units__company__admins=self.request.user).distinct()

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

        if not job.pk:
            job.save()
        [job.show_on_sites.add(s) for s in sites]
        print job.show_on_sites.all()
        return job


class JobAdmin(admin.ModelAdmin):
    exclude = ['guid', 'country_short', 'state_short']
    form = JobAdminForm
    list_display = ['__unicode__', 'guid']
    readonly_fields = ['date_new', 'date_updated']
    search_fields = ['title', 'company', 'show_on_sites__domain']

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