from django.contrib import admin

from postajob.forms import JobForm
from postajob.models import Job


class JobAdmin(admin.ModelAdmin):
    form = JobForm
    list_display = ('__unicode__', 'guid', )
    search_fields = ('title', 'company', 'show_on_sites__domain', )

    fieldsets = (
        ('Job Information', {
            'fields': (('title', 'is_syndicated'), 'reqid', 'description',
                       'city', 'state', 'country', 'zipcode',
                       ('date_expired', 'is_expired', 'autorenew', )),
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
        passed along to the JobForm.

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