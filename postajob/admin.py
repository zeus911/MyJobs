from django.contrib import admin
from django.forms import (CharField, ModelForm, ModelMultipleChoiceField,
                          Select)

from mydashboard.models import BusinessUnit, SeoSite
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

    def save(self, commit=True):
        job = super(JobAdminForm, self).save(commit)

        company = job.company
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

        job.buid = BusinessUnit.objects.filter(company=company)[0]
        job.generate_guid()

        if not job.pk:
            job.save()
        job.add_to_solr()
        return job


class JobAdmin(admin.ModelAdmin):
    exclude = ['guid', 'country_short', 'state_short', 'buid']
    form = JobAdminForm
    list_display = ['__unicode__', 'guid']
    readonly_fields = ['date_new', 'date_updated']
    search_fields = ['title', 'company', 'show_on_sites__domain']

    def delete_model(self, request, obj):
        obj.remove_from_solr()
        obj.delete()

admin.site.register(Job, JobAdmin)