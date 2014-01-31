from django.contrib import admin
from django.contrib.sites.models import Site

from myjobs.models import User, CustomHomepage, EmailLog
from myjobs.forms import UserAdminForm
from registration.models import ActivationProfile


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['email', 'event', 'received', 'processed']
    search_fields = ['email']
    list_filter = ['event','processed']


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'date_joined', 'last_response', 'is_active']
    search_fields = ['email']
    list_filter = ['is_active', 'is_disabled', 'is_superuser', 'is_staff']

    form = UserAdminForm
    readonly_fields = ('password', 'user_guid', 'last_response')
    exclude = ('profile_completion', )
    filter_horizontal = ['groups', 'user_permissions']
    fieldsets = [
        ('Password', {
            'fields': [
                ('password', 'password_change', ),
                ('new_password', )]}),
        ('Basic Information', {
            'fields': [
                ('email', 'gravatar', ),
                ('first_name', 'last_name', ),
                'user_guid', 'last_response', 'opt_in_employers',
                'opt_in_myjobs', ]}),
        ('Admin', {
            'fields': [
                ('user_permissions', 'groups', ),
                'is_active', 'is_superuser', 'is_staff', 'is_disabled']}),
    ]

admin.site.register(User, UserAdmin)
admin.site.register(ActivationProfile)
admin.site.register(CustomHomepage)
admin.site.register(EmailLog, EmailLogAdmin)
admin.site.unregister(Site)
