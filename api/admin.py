from django.contrib import admin
from api.models import APIUser, Industry, ViewSource

admin.site.register(ViewSource)


class APIUserAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created', 'date_disabled', 'key')
    list_display = ('company', 'key', 'first_name', 'last_name',
                    'email', 'phone', 'scope', 'jv_api_access', 'onet_access',
                    'view_source', 'date_created', 'date_disabled')

admin.site.register(APIUser, APIUserAdmin)
admin.site.register(Industry)
