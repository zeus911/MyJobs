from django.contrib import admin
from django.db.models import Q

from postajob.forms import JobForm, SitePackageForm
from postajob.models import Job, SitePackage


class ModelAdminWithRequest(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        """
        Override get_form() to allow the request information to be
        passed along to the JobForm.

        """
        ModelForm = super(ModelAdminWithRequest, self).get_form(request, obj,
                                                                **kwargs)

        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass


class JobAdmin(ModelAdminWithRequest):
    form = JobForm
    list_display = ('__unicode__', 'guid', )
    search_fields = ('title', 'company', 'site_packages__sites__domain', )

    fieldsets = (
        ('Job Information', {
            'fields': (('title', ), 'reqid', 'description',
                       'city', 'state', 'country', 'zipcode',
                       ('date_expired', 'is_expired', 'autorenew', )),
        }),
        ('Application Instructions', {
            'fields': ('apply_type', 'apply_link', 'apply_email',
                       'apply_info', ),
        }),
        ('Site Information', {
            'fields': ('company', 'post_to', 'site_packages', ),
        }),
    )

    def delete_model(self, request, obj):
        # Django admin bulk delete doesn't trigger a post_delete signal. This
        # ensures that the remove_from_solr() usually handled by a delete
        # signal is called in those cases.
        obj.remove_from_solr()
        obj.delete()

    def queryset(self, request):
        """
        Prevent users from seeing jobs that don't belong to their company
        in the admin.

        """
        jobs = super(JobAdmin, self).queryset(request)
        if not request.user.is_superuser:
            kwargs = {'company__admins': request.user}
            jobs = jobs.filter(**kwargs)
        return jobs


class SitePackageAdmin(ModelAdminWithRequest):
    form = SitePackageForm
    list_display = ('id', 'name', )

    def queryset(self, request):
        """
        Make SeoSite-specific packages unavailable in the admin and prevent
        non-superusers from seeing packages.

        """
        sites = SitePackage.objects.filter(sites=-1)
        if request.user.is_superuser:
            sites = SitePackage.objects.filter(seosite__isnull=True)
        return sites

admin.site.register(SitePackage, SitePackageAdmin)
admin.site.register(Job, JobAdmin)