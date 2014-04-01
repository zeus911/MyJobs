from django.contrib import admin

from django_extensions.admin import ForeignKeyAutocompleteAdmin

from mydashboard.models import CompanyUser


class CompanyUserAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('email', ),
        'company': ('name', ),
    }

    class Meta:
        model = CompanyUser


admin.site.register(CompanyUser, CompanyUserAdmin)
