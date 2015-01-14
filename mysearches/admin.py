from django.contrib import admin

from mysearches.models import SavedSearch, SavedSearchLog


class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'url', 'label', 'last_sent']
    search_fields = ['email', ]


class SavedSearchLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'was_sent', 'was_received', 'new_jobs',
                    'backfill_jobs']
    search_fields = ['recipient_email']
    list_filter = ['was_sent', 'was_received']

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
"""
    was_sent = models.BooleanField()
    was_received = models.BooleanField(default=False,
                                       help_text=("If date_sent is very "
                                       "recent and was_received is unchecked, "
                                       "SendGrid may not have responded yet - "
                                       "give it a few minutes."))
    reason = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recipient_email = models.EmailField(max_length=255, blank=False)
    new_jobs = models.IntegerField()
    backfill_jobs = models.IntegerField()
    date_sent = models.DateTimeField(auto_now_add=True)
    contact_record = models.ForeignKey('mypartners.ContactRecord', null=True,
                                       blank=True, on_delete=models.SET_NULL)
    uuid = models.CharField(max_length=32)"""
