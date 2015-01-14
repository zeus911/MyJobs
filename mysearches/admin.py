from django.contrib import admin

from mysearches.models import SavedSearch, SavedSearchLog


class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'url', 'label', 'last_sent']
    search_fields = ['email', ]


class SavedSearchLogAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        # Disable editing of existing saved search logs while allowing logs
        # to be added
        if obj is None:
            return self.readonly_fields
        else:
            return ('was_sent', 'was_received', 'reason', 'recipient',
                    'recipient_email', 'new_jobs', 'backfill_jobs',
                    'contact_record', 'date_sent')


admin.site.register(SavedSearch, SavedSearchAdmin)
admin.site.register(SavedSearchLog, SavedSearchLogAdmin)
