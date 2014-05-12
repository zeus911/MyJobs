from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField

from mydashboard.models import SeoSite
from postajob.models import Job


class JobAdminForm(ModelForm):
    class Meta:
        model = Job

    show_on_sites_widget = admin.widgets.FilteredSelectMultiple('Sites', False)
    show_on_sites = ModelMultipleChoiceField(SeoSite.objects.all(),
                                             required=False,
                                             widget=show_on_sites_widget)


class JobAdmin(admin.ModelAdmin):
    exclude = ['id', 'uid']
    form = JobAdminForm
    list_display = ['__unicode__']
    readonly_fields = ['date_new', 'date_updated']
    search_fields = ['title', 'company', 'show_on_sites__domain']

admin.site.register(Job, JobAdmin)