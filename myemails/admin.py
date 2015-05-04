from django.contrib import admin

from myemails import models
from myemails.forms import EventFieldForm


class CronEventAdmin(admin.ModelAdmin):
    form = EventFieldForm

    class Media:
        js = (
            'emails.js',
        )


class ValueEventAdmin(admin.ModelAdmin):
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