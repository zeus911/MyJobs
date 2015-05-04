from django.contrib import admin

from myemails import models
from myemails.forms import EventFieldForm


class RequestAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(RequestAdmin, self).get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest


class CronEventAdmin(RequestAdmin):
    fieldsets = [
        ('', {
            'fields': [
                'name',
                'email_template',
                'is_active',
                'owner',
                'sites',
            ]
        }),
        ('Comparison', {
            'description': (
                'Send an email after an amount of time has passed since an '
                'event occurred. The current options are for demonstration '
                'purposes only and may not be appropriate for actual events.'
            ),
            'fields': [
                'model',
                ('field', 'minutes'),
            ]
        }),
    ]
    form = EventFieldForm

    class Media:
        js = (
            'emails.js',
        )


class ValueEventAdmin(RequestAdmin):
    fieldsets = [
        ('', {
            'fields': [
                'name',
                'email_template',
                'is_active',
                'owner',
                'sites',
            ]
        }),
        ('Comparison', {
            'description': (
                'Send an email once a given criteria has been met. '
                'For example, entering "purchased product", "jobs_remaining", '
                '"is equal to", and "0" will be parsed as "send an email '
                'when someone has used up all of their allotted job postings."'
            ),
            'fields': [
                'model',
                ('field', 'compare_using', 'value'),
            ]
        }),
    ]
    form = EventFieldForm

    class Media:
        js = (
            'emails.js',
        )

admin.site.register(models.CronEvent, CronEventAdmin)
admin.site.register(models.ValueEvent, ValueEventAdmin)
admin.site.register(models.EmailTemplate)
admin.site.register(models.EmailSection)
